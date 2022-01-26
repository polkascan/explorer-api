#https://pythonspeed.com/articles/base-image-python-docker-images/
#FROM python:3.9-slim-buster
FROM python:3.8-buster

# install git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PYTHONPATH "${PYTHONPATH}:/usr/src"

## set working directory
RUN mkdir -p /usr/src
WORKDIR /usr/src

# Upgrade pip
RUN pip install --upgrade pip

## add requirements
COPY ./requirements_api.txt /usr/src/requirements.txt

## install requirements
RUN pip3 install -r requirements.txt

# add app
COPY . /usr/src

EXPOSE 8000

CMD bash -c "/usr/src/start-api.sh"
