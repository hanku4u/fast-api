"""
this file will contain the models for the database. each class will be a table in the database
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

# Define a User model class to represent a user in the database
class User(Base):
    __tablename__ = 'users'

    # Define columns for the user table
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    phone_number = Column(String)
    address_id = Column(Integer, ForeignKey('address.id'), nullable=True)

    # Define a relationship with the Todos model class
    todos = relationship('Todos', back_populates='owner')

    # Define a relationship with the Address model class
    address = relationship('Address', back_populates='user_address')


# Define a Todos model class to represent a to-do item in the database
class Todos(Base):
    __tablename__ = 'todos'

    # Define columns for the todos table
    id = Column(Integer, primary_key=True, index=True)
    title=Column(String)
    description=Column(String)
    priority=Column(Integer)
    completed=Column(Boolean, default=False)
    owner_id=Column(Integer, ForeignKey('users.id'))
    
    # Define a relationship with the User model class
    owner = relationship('User', back_populates='todos')


# Define an Address model class to represent an address in the database
class Address(Base):
    __tablename__ = 'address'

    # Define columns for the address table
    id = Column(Integer, primary_key=True, index=True)
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postalcode = Column(String)
    apt_num = Column(Integer)

    # Define a relationship with the User model class
    user_address = relationship('User', back_populates='address')
