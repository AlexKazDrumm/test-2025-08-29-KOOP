FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY uvicorn_config.py ./
EXPOSE 8000
CMD ["python", "uvicorn_config.py"]
