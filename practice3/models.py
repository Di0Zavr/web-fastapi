from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

class Teammate(SQLModel, table=True):
    team_id: int | None = Field(default=None, foreign_key="team.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)

class UserRole(Enum):
    user = "user"
    admin = "admin"
    organizer = "organizer"

class UserDefault(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    username: str 
    password: str
    email: str
    phone: str
    role: UserRole
    description: str | None = None
    avatar_url: str | None = None

class UserResponse(UserDefault):
    pass

class User(UserDefault, table=True):
    hackathons_organized: List["Hackathon"] | None = Relationship(back_populates="organizer", sa_relationship_kwargs={"cascade": "all, delete"})
    teams: List["Team"] | None = Relationship(back_populates="users", link_model=Teammate, sa_relationship_kwargs={"cascade": "all, delete"})

class HackathonDefault(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    participant_conditions: Optional[str] = ''
    location: str
    start_date: datetime
    end_date: datetime
    organizer_id: int | None = Field(default=None, foreign_key="user.id")

class HackathonResponse(HackathonDefault):
    organizer: User | None = None
    teams: List["Team"] | None = None

class Hackathon(HackathonDefault, table=True):
    organizer: User = Relationship(back_populates="hackathons_organized", sa_relationship_kwargs={"cascade": "all, delete"})
    teams: List["Team"] | None = Relationship(back_populates="hackathon", sa_relationship_kwargs={"cascade": "all, delete"})
    tasks: List["Task"] | None = Relationship(back_populates="hackathon", sa_relationship_kwargs={"cascade": "all, delete"})

class TeamDefault(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    hackathon_id: int | None = Field(default=None, foreign_key="hackathon.id")

class TeamResponse(TeamDefault):
    hackathon: Hackathon | None = None
    users: List[User] | None = None

class Team(TeamDefault, table=True):
    hackathon: Hackathon = Relationship(back_populates="teams", sa_relationship_kwargs={"cascade": "all, delete"})
    users: List[User] | None = Relationship(back_populates="teams", link_model=Teammate, sa_relationship_kwargs={"cascade": "all, delete"})

class TaskDefault(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    technical_task: str
    requirements: str | None = None
    grading_criteria: str | None = None
    hackathon_id: int = Field(default=None, foreign_key="hackathon.id")

class Task(TaskDefault, table=True):
    hackathon: Hackathon = Relationship(back_populates="tasks", sa_relationship_kwargs={"cascade": "all, delete"})
