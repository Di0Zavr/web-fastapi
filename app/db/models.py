from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

class UserRole(Enum):
    user = "user"
    admin = "admin"
    organizer = "organizer"

# defalt models

class UserDefault(SQLModel):
    username: str 
    password: str
    email: str
    phone: str
    role: UserRole
    description: str | None = None
    avatar_url: str | None = None

class HackathonDefault(SQLModel):
    organizer_id: int | None = Field(default=None, foreign_key="user.id")
    name: str
    description: str
    participant_conditions: Optional[str] = ''
    location: str
    start_date: datetime
    end_date: datetime

class TeamDefault(SQLModel):
    hackathon_id: int | None = Field(default=None, foreign_key="hackathon.id")
    name: str

class TaskDefault(SQLModel):
    hackathon_id: int | None = Field(default=None, foreign_key="hackathon.id") # hackid + taskid
    name: str
    description: str
    technical_task: str
    requirements: str | None = None
    grading_criteria: str | None = None

class TeamTaskSolutionDefault(SQLModel):
    team_id: int | None = Field(default=None, foreign_key="team.id")
    task_id: int | None = Field(default=None, foreign_key="task.id") # make hack_id + task_id
    review: str | None = None
    grade: str | None = None
    feedback: str | None = None

class SolutionFixDefault(SQLModel):
    solution_id: int | None = Field(default=None, foreign_key="teamtasksolution.id")
    commentary: str | None = None
    feedback: str | None = None

# table models

class Teammate(SQLModel, table=True):
    team_id: int = Field(foreign_key="team.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)

class User(UserDefault, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hackathons_organized: List["Hackathon"] | None = Relationship(back_populates="organizer", cascade_delete=True)
    teams: List["Team"] | None = Relationship(back_populates="users", link_model=Teammate)

class Hackathon(HackathonDefault, table=True):
    id: int | None = Field(default=None, primary_key=True)
    organizer: "User" = Relationship(back_populates="hackathons_organized")
    teams: List["Team"] | None = Relationship(back_populates="hackathon", cascade_delete=True)
    tasks: List["Task"] | None = Relationship(back_populates="hackathon", cascade_delete=True)

class Team(TeamDefault, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hackathon: "Hackathon" = Relationship(back_populates="teams")
    users: List["User"] | None = Relationship(back_populates="teams", link_model=Teammate)
    solutions: List["TeamTaskSolution"] | None = Relationship(back_populates="team", cascade_delete=True)

class Task(TaskDefault, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hackathon: "Hackathon" = Relationship(back_populates="tasks")
    solutions: List["TeamTaskSolution"] | None = Relationship(back_populates="task", cascade_delete=True)

class TeamTaskSolution(TeamTaskSolutionDefault, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team: "Team" = Relationship(back_populates="solutions")
    task: "Task" = Relationship(back_populates="solutions")
    fixes: List["SolutionFix"] = Relationship(back_populates="solution", cascade_delete=True)

class SolutionFix(SolutionFixDefault, table=True):
    id: int | None = Field(default=None, primary_key=True)
    solution: "TeamTaskSolution" = Relationship(back_populates="fixes")

# response models

class UserResponse(UserDefault):
    id: int | None = None

class HackathonResponse(HackathonDefault):
    id: int | None = None
    organizer: Optional["User"] = None

class TeamResponse(TeamDefault):
    id: int | None = None
    hackathon: Optional["Hackathon"] = None
    users: Optional[List["User"]] = None

class TaskResponse(TaskDefault):
    id: int | None = None
    hackathon: Optional["Hackathon"] = None

class TeamTaskSolutionResponse(TeamTaskSolutionDefault):
    id: int | None = None
    team: Optional["Team"] = None
    task: Optional["Task"] = None

class SolutionFixResponse(SolutionFixDefault):
    id: int | None = None
    solution: Optional["TeamTaskSolution"] = None

class UserLogin(SQLModel):
    username: str
    password: str
