import sys
sys.path.append("..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user, get_user_exception

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}},
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description="Priority must be between 1 and 5")
    completed: bool = False

@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@router.get("/user")
async def read_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()


@router.get("/{todo_id}")
async def read_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id"))\
        .first()
    
    if todo_model is not None:
        return todo_model
    else:
        raise http_exception()


@router.post("/")
async def create_todo(
        todo: Todo,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    if user is None:
        raise get_user_exception()
    
    todo_model = models.Todos(
        title=todo.title,
        description=todo.description,
        priority=todo.priority,
        completed=todo.completed,
        owner_id=user.get("id")
    )

    db.add(todo_model)
    db.commit()

    return success_response(201)


@router.put("/{todo_id}")
async def update_todo(
        todo_id: int,
        todo: Todo,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    if user is None:
        raise get_user_exception()
    
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id"))\
        .first()
    
    if todo_model is None:
        raise http_exception()
    
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.completed = todo.completed
    
    db.add(todo_model)
    db.commit()

    return success_response(200)


@router.delete("/{todo_id}")
async def delete_todo(
        todo_id: int,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    if user is None:
        raise get_user_exception()
    
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id"))\
        .first()
    
    if todo_model is None:
        raise http_exception()

    db.delete(todo_model)
    db.commit()

    return success_response(200)




def success_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }

def http_exception():
    return HTTPException(status_code=404, detail="Todo not found")


