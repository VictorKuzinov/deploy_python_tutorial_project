FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --upgrade pip "poetry==2.3.2"

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root --without dev

COPY . .

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]