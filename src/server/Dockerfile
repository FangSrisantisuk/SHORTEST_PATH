FROM python:3.10-slim as requirements-stage

# Set temp workdir in temp base image to install poetry and extract requirments.txt
WORKDIR /tmp

RUN pip install poetry
COPY src/server/pyproject.toml src/server/poetry.lock* /tmp/

# Extract requirements.txt from poetry
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Create a new image
FROM --platform=linux/amd64 python:3.10-slim

# Set app to workdir
WORKDIR /app

# Copy requirements.txt file from previous build stage
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

# Install Python Packages
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Install ODBC 17 Driver for Sql Server
RUN apt-get update  \
    && apt-get install -y curl apt-transport-https \
    && curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc \
    && curl https://packages.microsoft.com/config/debian/11/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Copy Source Code
COPY src/server/server /app

# Run entry Command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logging_conf.yaml"]
