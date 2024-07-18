FROM python:3.12-slim
COPY src/ ./
RUN ["pip", "install", "poetry"]
RUN ["poetry", "config", "virtualenvs.create", "false"]
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN ["poetry", "install"]
ENTRYPOINT ["python3", "main.py"]
