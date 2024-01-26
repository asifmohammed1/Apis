# main.py

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timedelta
from cachetools import TTLCache
import secrets

SQLALCHEMY_DATABASE_URL = "postgresql://sonuasif748:jBYaXx0NqOh8@ep-white-rain-379558.ap-southeast-1.aws.neon.tech/neondb"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
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

# SQLAlchemy Models
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

# FastAPI Application
app = FastAPI()

# OAuth2PasswordBearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT Secret Key (replace with a secure key in production)
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"

# Token expiration time
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Cache for response caching
cache = TTLCache(maxsize=1000, ttl=300)

# Dependency to get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Verify token here (e.g., decode JWT)
    # If token is invalid, raise credentials_exception
    # If token is valid, return the user
    return user

# Endpoint for user signup
@app.post("/signup", response_model=Token)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Implement user registration logic here (create user in the database)
    # Return a token upon successful signup
    return {"access_token": "some_random_token", "token_type": "bearer"}

# Endpoint for user login
@app.post("/login", response_model=Token)
async def login(user: UserCreate, db: Session = Depends(get_db)):
    # Implement user authentication logic here (verify email and password)
    # Return a token upon successful login
    return {"access_token": "some_random_token", "token_type": "bearer"}

# Endpoint to add a post
@app.post("/addPost", response_model=Post, dependencies=[Depends(get_current_user)])
async def add_post(post: PostCreate, db: Session = Depends(get_db)):
    # Implement post creation logic here (save post in the database)
    # Return the created post with a postID
    return {"id": 1, "text": post.text, "user_id": 1}

# Endpoint to get user posts
@app.get("/getPosts", response_model=list[Post], dependencies=[Depends(get_current_user)])
async def get_posts(db: Session = Depends(get_db)):
    # Implement logic to get user posts from the database
    # Cache the response using cachetools
    if "user_posts" in cache:
        return cache["user_posts"]
    else:
        user_posts = [{"id": 1, "text": "Sample Post", "user_id": 1}]  # Replace with actual database query
        cache["user_posts"] = user_posts
        return user_posts

# Endpoint to delete a post
# @app.delete("/deletePost/{post_id}", response_model=JSONResponse, dependencies=[Depends(get_current_user)])
# async def delete_post(post_id: int, db: Session = Depends(get_db)):
#     # Implement logic to delete the post from the database
#     # Return success or error response
#     return JSONResponse(content={"message": "Post deleted successfully"}, status_code=200)
