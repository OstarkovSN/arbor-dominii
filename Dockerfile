FROM python:3.10.2-slim

WORKDIR /harbour

RUN pip install poetry

COPY pyproject.toml /

COPY poetry.lock* /

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY /app /harbour/app

RUN mkdir /harbour/app/data && mkdir /harbour/app/data/raw

COPY company.tsv /harbour/app/data/raw/company.tsv

COPY founder_legal.tsv /harbour/app/data/raw/founder_legal.tsv

COPY founder_natural.tsv /harbour/app/data/raw/founder_natural.tsv

COPY main.py /harbour/

EXPOSE 1488

CMD ["poetry", "run", "python", "main.py"]