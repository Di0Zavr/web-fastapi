FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY migrations .
COPY alembic.ini .

EXPOSE 9000

CMD ["fastapi", "run", "app/app.py", "--port", "9000"]