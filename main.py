from fastapi import FastAPI, Depends
import models
from database import engine
from routers import auth, todos, address, users, admin
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)
app.include_router(address.router)
app.include_router(admin.router)

@app.get('/')
async def home():
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
