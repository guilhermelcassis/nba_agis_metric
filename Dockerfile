FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure the nba_data directory exists
RUN mkdir -p /app/nba_data

# Expose port 8080 for Fly.io
EXPOSE 8080

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=8080

# Use gunicorn as the production server
RUN pip install gunicorn

# Run the application using gunicorn
CMD gunicorn --bind 0.0.0.0:8080 app:app 