from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from cachetools import TTLCache
import secrets

DATABASE_URL = "postgres://sonuasif748:jBYaXx0NqOh8@ep-white-rain-379558.ap-southeast-1.aws.neon.tech/neondb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserCreate(BaseModel):
    email: str
    password: str

class User(UserCreate):
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class PostCreate(BaseModel):
    text: str

class Post(PostCreate):
    id: int
    user_id: int

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class PostModel(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

cache = TTLCache(maxsize=1000, ttl=300)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return user

@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    return {"access_token": "some_random_token", "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    return {"access_token": "some_random_token", "token_type": "bearer"}

@app.post("/addPost", response_model=Post, dependencies=[Depends(get_current_user)])
def add_post(post: PostCreate, db: Session = Depends(get_db)):
    return {"id": 1, "text": post.text, "user_id": 1}

@app.get("/getPosts", response_model=list[Post], dependencies=[Depends(get_current_user)])
def get_posts(db: Session = Depends(get_db)):
    if "user_posts" in cache:
        return cache["user_posts"]
    else:
        user_posts = [{"id": 1, "text": "Sample Post", "user_id": 1}]
        cache["user_posts"] = user_posts
        return user_posts

@app.delete("/deletePost/{post_id}", response_model=JSONResponse, dependencies=[Depends(get_current_user)])
def delete_post(post_id: int, db: Session = Depends(get_db)):
    return JSONResponse(content={"message": "Post deleted successfully"}, status_code=200)
