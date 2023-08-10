from datetime import timedelta, datetime
from starlette.responses import RedirectResponse
from typing import Annotated, Optional
from fastapi import APIRouter, Request, Response, Form
from fastapi.params import Depends
from fastapi import HTTPException
from pydantic import BaseModel
from database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Users
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError


from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")


templates = Jinja2Templates(directory="templates")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

SECRET_KEY = "54de6775831107b377b5d072873ce21b0399a654fbb8bec0365422f659a7c776"
ALGORITHM = "HS256"

class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def get_hash_password(password: str):
    return bcrypt_context.hash(password)

def verify_password(password: str, hashed_password: str):
    return bcrypt_context.verify(password, hashed_password)

def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.utcnow() + expires_delta
    encode["exp"] = expires

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            logout(request)
        return {"username": username, "id": user_id, "role": user_role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )



@router.post("/token/", status_code=status.HTTP_201_CREATED, response_model=Token)
async def login_for_access_token(
    response: Response,
    db: db_dependency,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = authenticate(form_data.username, form_data.password, db)

    if not user:
        return False
    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=60)
    )
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True


# Need to make two more routes that will be working with login and register templates and logics.


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
        validate_user_cookie = await login_for_access_token(
            response=response, form_data=form, db=db
        )

        if not validate_user_cookie:
            msg = "Incorrect username or password"
            return templates.TemplateResponse(
                "login.html", {"request": request, "msg": msg}
            )
        return response
    except HTTPException:
        msg = "Could not validate credentials"
        return templates.TemplateResponse(
            "login.html", {"request": request, "msg": msg}
        )


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    msg = "Logged out successfully."

    response = templates.TemplateResponse(
        "login.html", {"request": request, "msg": msg}
    )

    response.delete_cookie(key="access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    db: Session = Depends(get_db),
):
    
    exists = db.query(Users).filter(or_(Users.username == username, Users.email == email)).first() is not None
    
    if exists or password != password2:
        msg = "Invalid registeration request."
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg}
        )
    hash_password = get_hash_password(password)
    user_model = Users(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        hashed_password=hash_password,
        is_active=True,
    )
    db.add(user_model)
    db.commit()

    msg = "User created successfully."
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})