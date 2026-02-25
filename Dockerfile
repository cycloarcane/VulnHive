FROM python:3.12-slim

# Create a non-root user
RUN useradd -m -s /bin/bash appuser

WORKDIR /app

# Install ping for the RCE test, then clean up
RUN apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and set ownership to root so the non-root user cannot modify them
COPY . .
RUN chown -R root:root /app && chmod -R 555 /app

# Switch to the non-root user
USER appuser

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "app.py"]
