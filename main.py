from fastapi import FastAPI, Depends
import models
from database import engine
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status
from routers import auth, todos, users, address


# Creating an instance of the FastAPI application
app = FastAPI()

# Creating the database tables based on the models
models.Base.metadata.create_all(bind=engine)

# Mounting the static files folder to the application
app.mount("/static", StaticFiles(directory="static"), name="static")


# Adding a redirect to the root of the application
@app.get("/")
async def root():
    return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)

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
