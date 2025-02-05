FROM python:3.12

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     libclips-dev \
#     build-essential \
#     python3-dev \
#     && rm -rf /var/lib/apt/lists/*

WORKDIR /

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY app/ /app

CMD ["python3.12", "/app/main.py", "/data/input/simulated_endopheno_data.csv"]