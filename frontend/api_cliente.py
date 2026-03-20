import requests

BASE_URL = "http://127.0.0.1:8000/api/usuarios"

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
        