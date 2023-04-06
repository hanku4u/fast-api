import sys
sys.path.append("..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .auth import (
    get_current_user,
    get_user_exception,
    verify_password,
    get_password_hash
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@router.get("/{user_id}")
async def user_by_path(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is not None:
        return user
    return "Invalid user id"


@router.get("/user/")
async def user_by_query(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is not None:
        return user
    return "Invalid user id"


@router.put("/user/password")
async def user_password_change(user_verification: UserVerification, user: dict = Depends(get_current_user),
                                db: Session = Depends(get_db)):

    if user is None:
        raise get_user_exception()
    
    user_model = db.query(models.User).filter(models.User.id == user.get('id')).first()

    if user_model is not None:
        if user_verification.username == user_model.username and verify_password(
                user_verification.password,
                user_model.hashed_password):
            
            user_model.hashed_password = get_password_hash(user_verification.new_password)
            db.add(user_model)
            db.commit()
            return "Password changed"
    return "Invalid username or password"


@router.delete("/user")
async def delete_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    user_model = db.query(models.User).filter(models.User.id == user.get('id')).first()
    
    if user_model is None:
        return "Invalid user or request"
    
    db.query(models.User).filter(models.User.id == user.get('id')).delete()
    db.commit()

    return "User deleted"