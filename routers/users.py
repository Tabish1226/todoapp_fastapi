from fastapi import Depends, Form, HTTPException, Path, APIRouter, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Annotated
from database import SessionLocal
from starlette import status
from starlette.responses import RedirectResponse
from models import Users
from .auth import get_current_user, verify_password, get_hash_password
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="templates")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/me", status_code=status.HTTP_200_OK)
async def read_users(user: user_dependency, db: db_dependency):
    return db.query(Users).filter(Users.id == user.get("id")).all()



@router.get("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request})


@router.post("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(request: Request,username:str = Form(...), current_password: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.username == username).first()
    if user is not None:
        verify_pass = verify_password(current_password, user.hashed_password)
    if verify_pass:
        new_pass = get_hash_password(new_password)
    user.hashed_password = new_pass
    db.add(user)
    db.commit()


    msg = "Password changed successfully."
    return templates.TemplateResponse("change_password.html", {"request": request, "msg": msg})