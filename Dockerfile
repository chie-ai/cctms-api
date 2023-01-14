FROM bitnami/python:3.9-prod
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update -y 
RUN apt-get -y -f install build-essential sudo postgresql gunicorn libpq-dev postgresql-client curl \
    postgresql-client-common libncurses5-dev libjpeg-dev zlib1g-dev && \
    wget -O /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/8ed92e8cab83cfed76ff012ed4a36cef74b28096/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

RUN mkdir /home/project
RUN mkdir /home/project/backend/
RUN mkdir /home/project/backend/cctms/
RUN mkdir /home/project/backend/cctms/static
RUN mkdir /home/project/backend/cctms/media
WORKDIR /home/project/backend/cctms
COPY requirements.txt /home/project/backend/cctms/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /home/project/backend/cctms

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENTRYPOINT [ "sh", "entrypoint.sh" ]