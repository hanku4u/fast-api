from fastapi import FastAPI, Depends
import models                                   # import models from models.py
from database import engine                     # import engine from database.py
from routers import auth, todos                 # import auth and todos router from routers folder
from company import companyapis, dependencies   # import companyapis router from company folder

# Creating an instance of the FastAPI application
app = FastAPI()

# Creating the database tables based on the models
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)                 # Adding the auth router to the application
app.include_router(todos.router)                # Adding the todos router to the application

# Adding the companyapis router to the application
app.include_router(
    companyapis.router,
    prefix="/companyapis",
    tags=["companyapis"],
    dependencies=[Depends(dependencies.get_token_header)], 
    responses={418: {"description": "Internal Use Only"}},
    )