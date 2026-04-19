from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

USERNAME = "sonuasif748"
PASSWORD = "jBYaXx0NqOh8"
HOST = "ep-white-rain-379558.ap-southeast-1.aws.neon.tech"
DATABASE = "neondb"

URL_DATABASE = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}?sslmode=require'

engine = create_engine(URL_DATABASE, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()