FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libboost-python-dev \
    libboost-system-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

WORKDIR /app/src/web

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]