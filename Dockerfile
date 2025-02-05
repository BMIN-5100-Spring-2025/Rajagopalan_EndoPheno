FROM python:3.12

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     python3-dev \
#     libffi-dev \
#     clips \
#     libclips-dev  # Add this line to install the development files

# # Install CLIPS (C Language Integrated Production System)
# RUN apt-get update && apt-get install -y \
#     clips \
#     && rm -rf /var/lib/apt/lists/*

# # Install CLIPS from source (corrected URL and directory name)
# RUN wget https://files.pythonhosted.org/packages/5c/df/898982356541af065119211c0d8ae204ffec3e7053886fe4092fe0dc7e49/clipspy-1.0.4.tar.gz -O clips-1.0.4.tar.gz \
#     && tar -xvf clips-1.0.4.tar.gz \
#     && cd clipspy-1.0.4 \
#     && pip install . \
#     && cd .. \
#     && rm -rf clipspy-1.0.4 clips-1.0.4.tar.gz
WORKDIR /

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY app/ /app

CMD ["python3.12", "/app/main.py", "/data/input/simulated_endopheno_data.csv"]