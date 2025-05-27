FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Upgrade pip first to get latest resolver & features
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
