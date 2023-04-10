"""
This file contains the authentication routes and functions for FastAPI.
It handles user authentication by generating and verifying JWT access tokens, hashing
and verifying passwords using bcrypt, and managing user login and logout sessions.
Defines an APIRouter instance for handling authentication routes, as well as
several functions for handling database access and user authentication logic.
"""


import sys
sys.path.append("..")

from starlette.responses import RedirectResponse
from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Define a secret key and algorithm for generating JWT tokens
SECRET_KEY = "J8SEn9kuBbkPKYUDbyjy6S4rlO9eMomd"
ALGORITHM = "HS256"

# Create an instance of the Jinja2Templates class for rendering templates
templates = Jinja2Templates(directory="templates")

# Create an instance of the CryptContext class for hashing and verifying passwords
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Create an instance of the OAuth2PasswordBearer class for handling OAuth2 authentication
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')

# Create an instance of the APIRouter class for handling authentication routes
router = APIRouter(
    prefix='/auth', tags=['auth'],
    responses={401: {'description': 'Not authorized'}},
)

# Create the database tables if they do not already exist
models.Base.metadata.create_all(bind=engine)


# Define a LoginForm class for handling login form data
class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None 
        self.password: Optional[str] = None


    # Define an asynchronous method for populating the LoginForm instance with data from the request form
    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get('email')
        self.password = form.get('password')


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


# Define a function for hashing a password using bcrypt
def get_password_hash(password: str):
    return bcrypt_context.hash(password)


# Define a function for verifying a password against a hashed password using bcrypt
def verify_password(plain_password: str, hashed_password: str):
    return bcrypt_context.verify(plain_password, hashed_password)


# Define a function for authenticating a user based on their username and password
def authenticate_user(username: str, password: str, db: Session):

    # Query the database for the user with the specified username
    user = db.query(models.User).filter(models.User.username == username).first()

    # If no user is found, return False
    if not user:
        return False

    # If the user's password is not valid, return False
    if not verify_password(password, user.hashed_password):
        return False

    # If the user is found and the password is valid, return the user
    return user


# Define a function for creating a JWT access token
def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):

    # Define the payload for the token
    encode = {
        'sub': username,
        'id': user_id,
    }

    # If an expiration time is specified, set it in the payload
    if expires_delta:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=60)
    encode.update({'exp': expires_delta})

    # Encode the payload using the JWT library and return the token
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# Define an asynchronous function for retrieving the current user from a JWT token
async def get_current_user(request: Request):
    try:
        # Get the access token from the request cookie
        token = request.cookies.get('access_token')
        if token is None:
            return None

        # Decode the token and extract the username and user ID from the payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')

        # If the username or user ID are missing, log the user out and return None
        if username is None or user_id is None:
            logout(request)

        # Return the username and user ID as a dictionary
        return {'username': username, 'id': user_id}

    # If the token cannot be decoded, raise an HTTPException with a 404 status code
    except JWTError:
        raise HTTPException(status_code=404, detail="Not found")


# Define a route for handling login requests and creating JWT access tokens
@router.post('/token')
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):

    # Authenticate the user using the authenticate_user function
    user = authenticate_user(form_data.username, form_data.password, db)

    # If authentication fails, return False
    if not user:
        return False

    # Create a token expiration time of 60 minutes
    token_expires = timedelta(minutes=60)

    # Create an access token using the create_access_token function
    token = create_access_token(
        user.username,
        user.id,
        expires_delta=token_expires
    )

    # Set a cookie with the access token and a max age of 30 minutes
    response.set_cookie(key="access_token", value=token, max_age=1800 ,httponly=True)

    # Return True to indicate successful login
    return True


# Define a route for displaying the login page
@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):

    # Render the login.html template using the Jinja2Templates library and return the response
    return templates.TemplateResponse("login.html", {"request": request})


# Define a route for handling login requests
@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        # Create a LoginForm instance and use it to retrieve the username and password from the login form
        form = LoginForm(request)
        await form.create_oauth_form()

        # Create a RedirectResponse instance with a 302 status code and a URL to redirect to
        response = RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)

        # Call the login_for_access_token function with the response object, form data, and database object
        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        # If authentication fails, display an error message on the login page
        if not validate_user_cookie:
            msg = 'Incorrect username or password'
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

        # If authentication succeeds, redirect to the specified URL
        return response
    
    # If an unknown error occurs, display an error message on the login page
    except:
        msg = 'Unknown error'
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    

# Define a route for handling logout requests
@router.get("/logout")
async def logout(request: Request):

    # Set a success message to be displayed on the login page
    msg = 'Logout Successful'
    
    # Create a TemplateResponse instance with the login.html template and the success message
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})

    # Delete the access token cookie from the response
    response.delete_cookie(key='access_token')
    
    # Return the response
    return response


# Define a route for rendering the registration page
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):

    # Create a TemplateResponse instance with the register.html template and the request object
    return templates.TemplateResponse("register.html", {"request": request})


# Define a route for handling user registration requests
@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request,
                        email: str = Form(...),
                        username: str = Form(...),
                        firstname: str = Form(...),
                        lastname: str = Form(...),
                        password: str = Form(...),
                        password2: str = Form(...),
                        db: Session = Depends(get_db)
                        ):
    
    # Check if the username or email already exists in the database
    validation1 = db.query(models.User).filter(models.User.username == username).first()
    validation2 = db.query(models.User).filter(models.User.email == email).first()

    # If the passwords don't match or the username or email is already taken, render
    # the register.html template with an error message
    if password != password2 or validation1 is not None or validation2 is not None:
        msg = 'Invalid registration requestion'
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
    
    # If the input is valid, create a new user in the database
    user_model = models.User()
    user_model.email = email
    user_model.username = username
    user_model.first_name = firstname
    user_model.last_name = lastname

    hashed_password = get_password_hash(password)
    user_model.hashed_password = hashed_password
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    # Render the login.html template with a success message
    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
