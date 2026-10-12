FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY weather.py .

# Keep the container running or ready for Ofelia execution
CMD ["python", "weather.py"]

