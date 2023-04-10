"""
endoints for creating, updating and deleting todos
"""

import sys
sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse
from fastapi import Depends,  APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user

router = APIRouter(
    prefix="/todos",  # URL prefix for all endpoints in this router
    tags=["todos"],  # metadata for Swagger documentation
    responses={404: {"description": "Not found"}},  # default responses for all endpoints
)

models.Base.metadata.create_all(bind=engine)  # create the database tables using SQLAlchemy metadata

templates = Jinja2Templates(directory="templates")  # create a Jinja2 template engine instance for rendering HTML templates

def get_db():
    db = SessionLocal()
    try:
        yield db  # return the database session
    finally:
        db.close()  # close the database session after using it


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve all todos for the current user and render them using an HTML template
    """

    # validate users token
    user = await get_current_user(request)  # get the authenticated user from the request
    if user is None:
        # redirect to the login page if user is not authenticated
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    # query the database for all todos owned by the user
    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get('id')).all()

    # render the todos using an HTML template
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user": user})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo_page(request: Request):
    """
    Endpoint to render a form for adding a new todo
    """
    # validate users token
    user = await get_current_user(request)  # get the authenticated user from the request
    if user is None:
        # redirect to the login page if user is not authenticated
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    # render the add-todo form using an HTML template
    return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request: Request, title: str = Form(...), description: str = Form(...),
                        priority: str = Form(...), db: Session = Depends(get_db)):
    """
    Endpoint to create a new todo in the database and redirect to the home page
    """
    # validate users token
    user = await get_current_user(request)  # get the authenticated user from the request
    if user is None:
        # redirect to the login page if user is not authenticated
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    # create a new todo object and save it to the database
    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.completed = False
    todo_model.owner_id = user.get('id')

    db.add(todo_model)
    db.commit()

    # Redirect to home page
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_page(request: Request, todo_id: int, db: Session = Depends(get_db)):

    # validate users token
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id: int, title: str = Form(...), description: str = Form(...),
                        priority: str = Form(...), db: Session = Depends(get_db)):
    
    # Validate the user's token
    user = await get_current_user(request)
    if user is None:

        # If the user is not authenticated, redirect them to the authentication page
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
                        
    # Retrieve the todo item with the specified ID
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    # Update the todo item's attributes with the new values provided in the form data
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority

    # Add the modified todo item to the database and commit the changes
    db.add(todo_model)
    db.commit()

    # Return a redirect response that sends the user to the home page
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    # Validate the user's token
    user = await get_current_user(request)
    if user is None:

        # If the user is not authenticated, redirect them to the authentication page
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    # Retrieve the todo item with the specified ID and owner ID
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get('id'))\
        .first()

    # If the todo item is not found, redirect the user to the home page
    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    # Delete the todo item from the database and commit the changes
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    # Return a redirect response that sends the user to the home page
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    # Validate the user's token
    user = await get_current_user(request)
    if user is None:
        
        # If the user is not authenticated, redirect them to the authentication page
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    # Retrieve the todo item with the specified ID
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    # Toggle the `completed` attribute to the opposite of what it currently is
    todo.completed = not todo.completed

    # Add the modified todo item to the database and commit the changes
    db.add(todo)
    db.commit()

    # Return a redirect response that sends the user to the home page
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
