FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
ENTRYPOINT ["gunicorn"] 
CMD ["-w", "2", "-b", "0.0.0.0:8000", "app:app", "--preload", "--timeout", "10"]