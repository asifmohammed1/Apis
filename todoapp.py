from fastapi import FastAPI, HTTPException, Depends, status
# from fastapi.security import OAuth2PasswordBearer
# from fastapi.middleware.cors import CORSMiddleware
# from datetime import datetime
# from passlib.context import CryptContext
# from jose import JWTError, jwt
# import psycopg2
# from psycopg2 import sql
# from typing import List
# from datetime import timedelta
# import secrets

# # Replace with your PostgreSQL connection string
# DATABASE_URL = "postgres://sonuasif748:jBYaXx0NqOh8@ep-white-rain-379558.ap-southeast-1.aws.neon.tech/neondb"

# # FastAPI app instance
app = FastAPI()

# # CORS Middleware to allow cross-origin requests
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # JWT token settings
# SECRET_KEY = secrets.token_urlsafe(32)
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

@app.get("/test")
def register_user():
    return {"message": "testing"}