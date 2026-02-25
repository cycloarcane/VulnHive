FROM python:3.12-slim

WORKDIR /app

# Install ping for the RCE test
RUN apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# We use python directly to run the TUI, it requires a pseudo-TTY when running the container
CMD ["python", "app.py"]
