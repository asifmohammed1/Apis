from fastapi import FastAPI, HTTPException, Depends, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import psycopg2
from psycopg2 import sql
from typing import List

# Replace with your PostgreSQL connection string
DATABASE_URL = "postgres://sonuasif748:jBYaXx0NqOh8@ep-white-rain-379558.ap-southeast-1.aws.neon.tech/neondb"

# FastAPI app instance
app = FastAPI()

# CORS Middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT token settings
SECRET_KEY = "your-secret-key"  # Replace with a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to create a database connection
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        conn.close()


# Functions to work with JWT tokens
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return username


# API to create a new user
@app.post("/register")
def register_user(username: str, email: str, password: str, db: psycopg2.extensions.cursor = Depends(get_db)):
    # Hash the password before storing it in the database
    hashed_password = pwd_context.hash(password)

    # Insert new user into the users table
    insert_query = sql.SQL("INSERT INTO users (username, email, password_hash) VALUES ({}, {}, {});").format(
        sql.Literal(username),
        sql.Literal(email),
        sql.Literal(hashed_password)
    )
    db.execute(insert_query)
    return {"message": "User registered successfully"}


# API to authenticate and generate JWT token
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = authenticate_user(db, form_data.username, form_data.password)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# API to get the current user's profile
@app.get("/users/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user


# API to create a new task
@app.post("/tasks")
def create_task(task: dict, db: psycopg2.extensions.cursor = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Insert new task into the tasks table
    insert_query = sql.SQL("""
        INSERT INTO tasks (user_id, title, description, due_date, is_completed) 
        VALUES ({}, {}, {}, {}, {});
    """).format(
        sql.Literal(current_user["user_id"]),
        sql.Literal(task["title"]),
        sql.Literal(task.get("description")),
        sql.Literal(task.get("due_date")),
        sql.Literal(task.get("is_completed", False))
    )
    db.execute(insert_query)
    return {"message": "Task created successfully"}


# API to get all tasks for the current user
@app.get("/tasks", response_model=List[dict])
def read_tasks(skip: int = 0, limit: int = 100, db: psycopg2.extensions.cursor = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Select tasks for the current user
    select_query = sql.SQL("""
        SELECT * FROM tasks 
        WHERE user_id = {}
        OFFSET {}
        LIMIT {};
    """).format(
        sql.Literal(current_user["user_id"]),
        sql.Literal(skip),
        sql.Literal(limit)
    )
    db.execute(select_query)
    tasks = db.fetchall()
    return tasks


# API to update a task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: dict, db: psycopg2.extensions.cursor = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Update task in the tasks table
    update_query = sql.SQL("""
        UPDATE tasks
        SET title = {}, description = {}, due_date = {}, is_completed = {}
        WHERE task_id = {} AND user_id = {};
    """).format(
        sql.Literal(task["title"]),
        sql.Literal(task.get("description")),
        sql.Literal(task.get("due_date")),
        sql.Literal(task.get("is_completed", False)),
        sql.Literal(task_id),
        sql.Literal(current_user["user_id"])
    )
    db.execute(update_query)
    return {"message": "Task updated successfully"}


# # API to delete a task
# @app.delete("/tasks/{task_id}")
# def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     db_task = db.query(Task).filter(Task.task_id == task_id, Task.user_id == current_user.user_id).first()
#     if db_task is None:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     db.delete(db_task)
#     db.commit()
    
#     return {"message": "Task deleted successfully"}
