FROM python:3.12.3-slim

RUN apt-get update && \
    apt-get install -y \
        unar \
        git \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /CS2_Project

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN mkdir -p /CS2_Project/data/rars
RUN mkdir -p /CS2_Project/data/demos

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]