from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
from dotenv import dotenv_values

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

# Load environment variables from .env file
env_vars = dotenv_values(".env")
sqlite_url = env_vars.get("SQLITE_URL")

# Create SQLAlchemy engine
engine = create_engine(sqlite_url)

# Function to create database tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    create_db_and_tables()
    yield

# Create FastAPI app instance
app: FastAPI = FastAPI(lifespan=lifespan)

# Route to create a new task
@app.post("/task/")
def create_task(task: Task):
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

# Route to retrieve all task
@app.get("/task/")
def read_task():
    with Session(engine) as session:
        task = session.exec(select(Task)).all()
        return task