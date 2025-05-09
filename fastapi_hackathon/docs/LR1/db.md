# База данных

Для проекта используется база данных PostgreSQL 15, которая разворачивается в docker-контейнере. Для взаимодействия приложения с базой данных используется ORM система SQlModel. Настройка миграций осуществляется через библиотеку Alembic.

Настройка базы данных осуществляется в файле db/db.py

<details>
<summary>db.py</summary>

```python
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
import os

load_dotenv('app/.env')

db_url = os.getenv("POSTGRES_URL")
engine = create_engine(db_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

</details>

Файл содержит функции для инициализации базы данных, которая вызывается на старте веб-приложения, и генератор сессии для доступа к базе.

При инициализации базы данных создаются таблицы всех сущностей, которые были объявлены в коде.
