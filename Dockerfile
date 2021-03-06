# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Select which storage service to use
ENV CONDUCTOR_STORAGE_TYPE="ETCD"

# For service based storage, specify hostname and port
ENV CONDUCTOR_STORAGE_HOST="localhost"
ENV CONDUCTOR_STORAGE_PORT="2379"

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

VOLUME /app/data

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "service.conductor:api"]
