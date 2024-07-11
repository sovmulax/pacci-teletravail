FROM ubuntu:22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update package repository and install required packages
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install -y python3 python3-pip postgresql-client postgresql-server-dev-all gcc g++ \
    curl nano netcat libldap2-dev libsasl2-dev libssl-dev

# Upgrade pip and install gunicorn
RUN pip3 install --upgrade pip
RUN pip3 install gunicorn

# Create working directory
WORKDIR /home/app

# Copy requirements and install them
COPY ./requirements.txt /home/app/
RUN pip3 install -r requirements.txt

# Copy your application files
COPY ./app /home/app
COPY ./docker /home/app/docker

# Make entrypoint scripts executable
RUN chmod +x /home/app/docker/backend/server-entrypoint.sh
