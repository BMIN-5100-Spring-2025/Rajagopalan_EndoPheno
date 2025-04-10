FROM python:3.12-slim

WORKDIR /

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY app/ /app

CMD ["python3.12", "/app/main.py", "/data/input/simulated_endopheno_data.csv"]