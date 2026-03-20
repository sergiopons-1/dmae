import requests

BASE_URL = "http://127.0.0.1:8000/api/usuarios"
BASE_URL_API = "http://127.0.0.1:8000/api"

def login(username, password):
    try:
        r = requests.post(f"{BASE_URL}/login/", json={
            "username": username,
            "password": password
        }, timeout=5)
        return r.status_code, r.json()
    except requests.exceptions.ConnectionError:
        return None, {"error": "No se puede conectar al servidor"}

def singin(username, password, email, first_name, last_name):
    try:
        r = requests.post(f"{BASE_URL}/registro/", json={
            "username": username, "password": password,
            "email": email, "first_name": first_name,
            "last_name": last_name
        }, timeout=5)
        return r.status_code, r.json()
    except requests.exceptions.ConnectionError:
        return None, {"error": "No se puede conectar al servidor"}


def obtener_pacientes_clinica(clinic_id, token=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = requests.get(
            f"{BASE_URL_API}/pacientes/por_clinica/",
            params={"clinic_id": clinic_id},
            headers=headers,
            timeout=5,
        )
        return r.status_code, r.json()
    except requests.exceptions.ConnectionError:
        return None, {"error": "No se puede conectar al servidor"}
        