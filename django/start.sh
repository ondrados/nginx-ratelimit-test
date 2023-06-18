#!/bin/sh

echo "Waiting for database..."
while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.1
done
echo "Database available"


python manage.py makemigrations
python manage.py migrate
#python manage.py collectstatic --no-input --clear

python manage.py runserver 0.0.0.0:8000
