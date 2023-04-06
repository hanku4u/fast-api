from fastapi import FastAPI, Depends
import models                                   # import models from models.py
from database import engine                     # import engine from database.py
from routers import (                           # import routers from routers folder
            auth,
            todos,
            users,
            address
            )

# Creating an instance of the FastAPI application
app = FastAPI()

# Creating the database tables based on the models
models.Base.metadata.create_all(bind=engine)

# adding the routers to the application for auth, todos, and users
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
app.include_router(address.router)

# example of adding prefix, tags, dependencies, and responses to a router
# app.include_router(
#     companyapis.router,
#     prefix="/companyapis",
#     tags=["companyapis"],
#     dependencies=[Depends(dependencies.get_token_header)], 
#     responses={418: {"description": "Internal Use Only"}},
#     )
