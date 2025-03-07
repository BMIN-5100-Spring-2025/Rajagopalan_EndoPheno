FROM python:3.12-slim

WORKDIR /

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY app/ /app

CMD ["python3.12", "/app/main.py", "/data/input/simulated_endopheno_data.csv"]