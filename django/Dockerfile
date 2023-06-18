# pull official base image
FROM python:3.11-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/src

# install system dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev netcat-openbsd \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# install python dependencies
COPY ./requirements.txt /usr/src/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf requirements.txt

# copy project
COPY . /usr/src/

# run server
CMD ["/usr/src/start.sh"]
