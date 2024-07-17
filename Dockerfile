FROM python:3.12-slim
COPY src/ ./
ENTRYPOINT ["python3", "main.py"]
