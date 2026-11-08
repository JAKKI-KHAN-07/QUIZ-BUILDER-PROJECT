from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from database import Base

class QuizRequest(BaseModel):
    topic: str
    difficulty: str
    num_questions: int

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)