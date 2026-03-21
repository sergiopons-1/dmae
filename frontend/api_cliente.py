import requests

BASE_URL = "http://127.0.0.1:8000/api/usuarios"
BASE_URL_API = "http://127.0.0.1:8000/api"


def _network_error_response(exc):
    if isinstance(exc, requests.exceptions.Timeout):
        return None, {"error": "El servidor tardó demasiado en responder"}
    if isinstance(exc, requests.exceptions.ConnectionError):
        return None, {"error": "No se puede conectar al servidor"}
    return None, {"error": "Error de red al comunicarse con el servidor"}

def login(username, password):
    try:
        r = requests.post(f"{BASE_URL}/login/", json={
            "username": username,
            "password": password
        }, timeout=10)
        return r.status_code, r.json()
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)

def singin(username, password, email, first_name, last_name):
    try:
        r = requests.post(f"{BASE_URL}/registro/", json={
            "username": username, "password": password,
            "email": email, "first_name": first_name,
            "last_name": last_name
        }, timeout=10)
        return r.status_code, r.json()
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)


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
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)
        

def singin_paciente(username, dni, email, first_name, last_name, birth_date, token=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = requests.post(f"{BASE_URL}/registro-paciente/", json={
            "username": username,
            "dni": dni,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
        }, headers=headers, timeout=10)
        return r.status_code, r.json()
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)