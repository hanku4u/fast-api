from fastapi import FastAPI, Depends
import models                                   # import models from models.py
from database import engine                     # import engine from database.py
from routers import auth, todos, users          # import auth and todos router from routers folder
from company import companyapis, dependencies   # import companyapis router from company folder

# Creating an instance of the FastAPI application
app = FastAPI()

# Creating the database tables based on the models
models.Base.metadata.create_all(bind=engine)

# adding the routers to the application for auth, todos, and users
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
app.include_router(
    companyapis.router,
    prefix="/companyapis",
    tags=["companyapis"],
    dependencies=[Depends(dependencies.get_token_header)], 
    responses={418: {"description": "Internal Use Only"}},
    )
