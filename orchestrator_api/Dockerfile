FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Sherlock
RUN git clone https://github.com/sherlock-project/sherlock.git /opt/sherlock
WORKDIR /opt/sherlock
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app
RUN ln -s /opt/sherlock/sherlock /usr/local/bin/sherlock

COPY . .

# Default command can be overridden in docker-compose
CMD ["python", "main.py"]
