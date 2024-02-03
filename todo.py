from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pydantic import BaseModel
# from typing import List, Annotated
import models
from database import engine,SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import secrets
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

loginapis = APIRouter(prefix="/auth", tags=["Login API's"])
todoapis = APIRouter(prefix="/todo", tags=["Todo API's"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(BaseModel):
    username: str
    email: str
    password_hash: str

class TodoBase(BaseModel):
    task: str
    # id: int
    user_id: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# db_dependency = Annotated[Session, Depends(get_db)]

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.Userss).filter(models.Userss.username == username).first()

    if user and pwd_context.verify(password, user.password_hash):
        return user
    return None

def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise credentials_exception


# Auth API's
@loginapis.get("/Listofusers")
async def AllUser(db: Session = Depends(get_db)):
    result = db.query(models.Userss).all()
    return result

@loginapis.get("/getuser")
async def UserDetails(user_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Userss).filter(models.Userss.user_id == user_id).first()
    return result

@loginapis.post("/token")
async def login_for_access_token(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.Userss).filter(models.Userss.username == username).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@loginapis.post("/Register")
async def register_user(req: UserBase, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(req.password_hash)
    db_user = models.Userss(username=req.username,password_hash=hashed_password,email=req.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# TODO API's
# @todoapis.get("/list")
# async def TodoDetails(todo_id: int, db: Session = Depends(get_db)):
#     result = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
#     return result
#
@todoapis.post("/create")
async def create_todo(req: TodoBase, db: Session = Depends(get_db)):
    user = db.query(models.Userss).filter(models.Userss.user_id == 6).first()
    db_todo = models.Todo(task=req.task, user_id=77)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@todoapis.get("/list")
async def todo_details(todo_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    result = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Todo not found")

# @todoapis.post("/create")
# async def create_todo(req: TodoBase, db: Session = Depends(get_db), token: str = Depends(verify_token)):
#     user = db.query(models.Userss).filter(models.Userss.username == token).first()
#     if not user:
#         raise HTTPException(status_code=401, detail="Unauthorized")
#
#     db_todo = models.Todo(task=req.task, user_id=user, id=req.id)
#     db.add(db_todo)
#     db.commit()
#     db.refresh(db_todo)
#     return db_todo