# Foodgram API

## Project description:

The Foodgram project allows users to share their recipes. Users can subscribe for each other, add recipes to favorite and to shopping cart. Users also can download shopping list in a convenient form.

Interaction with the database is carried out through the Api.

The list of requests and endpoints is described in the ReDoc documentation, available at:

```
http://127.0.0.1:8000/redoc/
```

## Stack:
- Django 3.2
- DRF 3.12.4
- djangorestframework-simplejwt 4.7.2
- PyJWT 2.1.0
- PostgreSQL

## Filling template .env:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

## Project launch:
Clone the repository:

```
git clone git@github.com:Sheleg0v/yamdb_final
```

Change directory on the command line:

```
cd backend/foodgram_backend/infra_dev
```

launch docker-compose

```
docker-compose up -d --build
```

Change directory on the command line:

```
cd ../backend/foodgram_backend
```

launch django server

```
python manage.py runserver
```

Apply migrations:

```
python manage.py makemigrations
```
```
python manage.py migrate
```

### Author:
- https://github.com/Sheleg0v - Ivan Shelegov
