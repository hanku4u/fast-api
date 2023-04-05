from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    todos = relationship('Todos', back_populates='owner')

class Todos(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    title=Column(String)
    description=Column(String)
    priority=Column(Integer)
    completed=Column(Boolean, default=False)
    owner_id=Column(Integer, ForeignKey('users.id'))
    
    owner = relationship('User', back_populates='todos')