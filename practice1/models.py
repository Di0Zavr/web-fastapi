from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel

class UserRole(Enum):
    user = "user"
    admin = "admin"
    organizer = "organizer"

class User(BaseModel):
    id: int
    username: str
    password: str
    email: str
    phone: str
    role: UserRole

class Task(BaseModel):
    id: int
    name: str
    description: str
    technical_task: str
    requirements: Optional[str] = ''
    grading_criteria: Optional[str] = ''

class Hackathon(BaseModel):
    id: int
    name: str
    description: str
    participant_conditions: Optional[str] = ''
    location: str
    organizer: User
    start_date: datetime
    end_date: datetime
    tasks: Optional[List[Task]] = []
