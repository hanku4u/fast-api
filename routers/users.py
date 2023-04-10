"""
This file contains the API endpoints for managing user passwords.
"""

import sys
sys.path.append('..')

from starlette import status
from starlette.responses import RedirectResponse
from fastapi import Depends, APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .auth import get_current_user, verify_password, get_password_hash

# Create a new APIRouter instance with the prefix "/users" and the tag "users"
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# Create the database tables if they do not already exist
models.Base.metadata.create_all(bind=engine)

# Create an instance of the Jinja2Templates class for rendering templates
templates = Jinja2Templates(directory="templates")

# Define a function for getting a database session
def get_db():
    # Create a SessionLocal instance
    db = SessionLocal()
    try:
        # Yield the session to the calling function
        yield db
    finally:
        # Close the session when the function is done
        db.close()


# Define a Pydantic model for user verification data
class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str


@router.get("/edit-password", response_class=HTMLResponse)
async def edit_user_view(request: Request):
    """
    authenticate the user and then render the "edit-user-password.html" template
    """

    # Retrieve the current user from the request
    user = await get_current_user(request)
    
    # If the user is not authenticated, redirect them to the authentication page
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    # Render the "edit-user-password.html" template and pass in the request and user objects
    return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user})


@router.post("/edit-password", response_class=HTMLResponse)
async def user_password_change(request: Request,
                                username: str = Form(...),
                                password: str = Form(...),
                                password2: str = Form(...),
                                db: Session = Depends(get_db)
                                ):
    
    """
    authenticate the user and then change their password
    """
    
    # Validate the user's token
    user = await get_current_user(request)
    
    # If the user is not authenticated, redirect them to the authentication page
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    # Retrieve the user data from the database based on the specified username
    user_data = db.query(models.User).filter(models.User.username == username).first()

    # Set a default error message
    msg = "Invalid username or password"

    # If the user data is found and the password is correct, update the password in the database
    if user_data is not None:
        if username == user_data.username and verify_password(password, user_data.hashed_password):
            user_data.hashed_password = get_password_hash(password2)
            db.add(user_data)
            db.commit()
            msg = "Password changed successfully"

    # Render the "edit-user-password.html" template and pass in the request, user, and message objects
    return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user, "msg": msg})
