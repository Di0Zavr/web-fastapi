# Модели

Модели объектов, которые используются в базе данных. Описание моделей содержится в файле db/models.py

<details>
<summary>models.py</summary>
```python
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

class UserRole(Enum):
    user = "user"
    admin = "admin"
    organizer = "organizer"

// defalt models

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

// table models

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

// response models

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

// auth models

class UserLogin(SQLModel):
    username: str
    password: str

class UserUpdate(SQLModel):
    phone: str
    role: UserRole
    description: str | None
    avatar_url: str | None

```

</details>

## User

Модель пользователя, который взаимодействует с системой. Содержит поля:

- id - (PK) уникальный идентификатор
- username - уникальное имя пользователя
- password - пароль (хеш) пользователя
- email - адрес электронной почты
- phone - номер телефона
- role - роль пользователя в приложении (user, organizer, admin)
- description - подробная информация о пользователе
- avatar_url - url на аватарку пользователя

## Hackathon

Модель хакатона - информация о мероприятии. Содержит поля:

- id - (PK) уникальный идентификатор
- organizer_id - (FK) id пользователя-организатора
- name - название мероприятия
- description - описание мероприятия
- participant_conditions - условия участия
- location - место проведения
- start_date - дата начала
- end_date - дата конца

## Team

Модель команды, которая зарегистрировалась на хакатон. Содержит поля:

- id - (PK) уникальный идентификатор
- hackathon_id - (FK) id хакатон, на который зарегистрировалась команда
- name - название команды

## Teammate

Ассоциативная таблица между Team и User, содержит информация о нахождении пользователей в командах. Содержит поля:

- team_id (PK)(FK) - id команды
- user_id (PK)(FK) - id пользователя

## Task

Модель задания для хакатона. Содержит поля:

- id - (PK) уникальный идентификатор
- hackathon_id - (FK) id хакатона
- name - название задания
- description - описание задания
- technical_task - описание ТЗ к заданию
- requirements - требования к участникам
- grading_criteria - критерии оценки решений задания

## TeamTaskSolution

Модель решения задания командой. Содержит поля:

- id - (PK) - уникальный идентификатор
- team_id - (FK) id команды
- task_id - (FK) id задания
- review - описание решения, ссылки на результаты работы
- grade - оценка решения
- feedback - обратная связь от организаторов по решению

## SolutionFix

Модель правки по решению. Содержит поля:

- id - (PK) уникальный идентификатор
- solution_id (FK) id решения
- commentary - комментарий команды по правке
- feedback - обратная связь от организатора по правке
