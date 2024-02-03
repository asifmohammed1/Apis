from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

class Userss(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    username = Column(String, index=True)
    password_hash = Column(String, index=True)


class Todo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("Users.id"))