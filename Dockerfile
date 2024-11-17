FROM python:3.10.2-slim

WORKDIR /harbour

RUN pip install poetry

COPY pyproject.toml /

COPY poetry.lock* /

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY /app /harbour/app

COPY main.py /harbour/

COPY flags/docker=True.flag /harbour/docker.flag

EXPOSE 1488

CMD ["poetry", "run", "python", "main.py"]