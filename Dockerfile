FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["gunicorn"] 
CMD ["-w", "4", "-b", "0.0.0.0:8000", "app:app"]