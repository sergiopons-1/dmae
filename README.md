# DMAE

Aplicación de rehabilitación y seguimiento para personas con DMAE. Está realizada con PyQt6 para frontend, Django para backend y con la base de datos SQLite.

## Requisitos

- Python 3.12 o superior
- Git
- Windows

## Instalación

### 1. Crear y activar un entorno virtual

Desde la raíz del proyecto:

```bash
python -m venv .venv
```

En Windows con `cmd`:

```bat
.venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Preparar la base de datos

Desde la carpeta `backend`:

```bash
cd backend
py manage.py makemigrations
py manage.py migrate
py manage.py poblar_bd
```

Si aparece un error de historial inconsistente de migraciones en desarrollo, borra `backend/db.sqlite3` y vuelve a ejecutar `py manage.py migrate`.

## Arrancar el backend

Desde `backend`:

```bash
py manage.py runserver
```

## Arrancar el frontend

Desde otra terminal, con el entorno virtual activo y desde la raíz del proyecto:

```bash
cd frontend
py main.py
```

## Notas

- El backend usa `localhost:8000` por defecto.
- El frontend consume la API local y espera que el backend esté levantado antes de abrir la aplicación.