# Arrancar el proyecto

## Poblar base de datos:

```
cd backend
py manage.py makemigrations
py manage.py migrate
py manage.py poblar_bd
```

## Lanzar backend

```
py manage.py runserver
```

## Lanzar frontend. 

Desde otro terminal

```
cd frontend
py main.py
```