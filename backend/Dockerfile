FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential
ENV PYTHONUNBUFFERED 1

WORKDIR /django

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# RUN pip install --upgrade pip

# COPY requirements.txt requirements.txt

COPY . .

# Ensure the entrypoint script is executable
RUN chmod +x /django/entrypoint.sh

# Default command to run the entrypoint script
CMD ["sh", "/django/entrypoint.sh"]