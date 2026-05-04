import requests

BASE_URL = "http://127.0.0.1:8000/api/usuarios"
BASE_URL_API = "http://127.0.0.1:8000/api"
BASE_URL_EYE = "http://127.0.0.1:8000/api/eye-tracking"

_AUTH_EXPIRED_HANDLER = None


def set_auth_expired_handler(handler):
    global _AUTH_EXPIRED_HANDLER
    _AUTH_EXPIRED_HANDLER = handler


def _notify_auth_expired():
    if callable(_AUTH_EXPIRED_HANDLER):
        _AUTH_EXPIRED_HANDLER()


def _network_error_response(exc):
    if isinstance(exc, requests.exceptions.Timeout):
        return None, {"error": "El servidor tardó demasiado en responder"}
    if isinstance(exc, requests.exceptions.ConnectionError):
        return None, {"error": "No se puede conectar al servidor"}
    return None, {"error": "Error de red al comunicarse con el servidor"}


def _normalize_error_payload(status_code, payload):
    if status_code is not None and 200 <= status_code < 300:
        return payload

    if not isinstance(payload, dict):
        return {"error": "Error inesperado del servidor"}

    if "error" in payload:
        return payload

    # DRF/SimpleJWT suele responder con "detail" en errores de autenticacion.
    detail = payload.get("detail")
    if status_code == 401 and detail:
        return {"error": "Sesion no valida o caducada. Inicia sesion de nuevo."}

    if detail:
        return {"error": str(detail)}

    return payload

def login(username, password):
    try:
        r = requests.post(f"{BASE_URL}/login/", json={
            "username": username,
            "password": password
        }, timeout=10)
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)


def logout(refresh_token, token=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = requests.post(
            f"{BASE_URL}/logout/",
            json={"refresh": refresh_token},
            headers=headers,
            timeout=10,
        )
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)

def singin(username, password, email, first_name, last_name, clinic_id):
    try:
        r = requests.post(f"{BASE_URL}/registro/", json={
            "username": username, "password": password,
            "email": email, "first_name": first_name,
            "last_name": last_name,
            "clinic_id": clinic_id,
        }, timeout=10)
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)


def obtener_clinicas():
    try:
        r = requests.get(f"{BASE_URL}/clinicas/", timeout=10)
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
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
            timeout=10,
        )
        if r.status_code == 401:
            _notify_auth_expired()
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
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
        if r.status_code == 401:
            _notify_auth_expired()
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)


def cambiar_contrasena_especialista(password, token=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = requests.post(
            f"{BASE_URL}/cambiar-contrasena/",
            json={"password": password},
            headers=headers,
            timeout=10,
        )
        if r.status_code == 401:
            _notify_auth_expired()
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)


def obtener_progreso_individual(paciente_id, token=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = requests.get(
            f"{BASE_URL_API}/pacientes/{paciente_id}/progreso_individual/",
            headers=headers,
            timeout=10,
        )
        if r.status_code == 401:
            _notify_auth_expired()
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)


def crear_nota(paciente_id, contenido, token=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = requests.post(
            f"{BASE_URL_API}/pacientes/{paciente_id}/crear_nota/",
            json={"contenido": contenido},
            headers=headers,
            timeout=10,
        )
        if r.status_code == 401:
            _notify_auth_expired()
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)


def obtener_mi_progreso(token=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = requests.get(
            f"{BASE_URL}/mi-progreso/",
            headers=headers,
            timeout=10,
        )
        if r.status_code == 401:
            _notify_auth_expired()
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)


def iniciar_rehabilitacion(token=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = requests.post(
            f"{BASE_URL}/iniciar-rehabilitacion/",
            headers=headers,
            timeout=10,
        )
        if r.status_code == 401:
            _notify_auth_expired()
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)


def obtener_detalle_rehabilitacion(id_rehabilitacion, token=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = requests.get(
            f"{BASE_URL}/rehabilitacion/{id_rehabilitacion}/detalle/",
            headers=headers,
            timeout=10,
        )
        if r.status_code == 401:
            _notify_auth_expired()
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)


def registrar_puntuacion_edificio(edificio, puntuacion, token=None, id_rehabilitacion=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        body = {"edificio": edificio, "puntuacion": puntuacion}
        if id_rehabilitacion is not None:
            body["idRehabilitacion"] = id_rehabilitacion

        r = requests.post(
            f"{BASE_URL}/registrar-puntuacion-edificio/",
            json=body,
            headers=headers,
            timeout=10,
        )
        if r.status_code == 401:
            _notify_auth_expired()
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)


def obtener_ajustes_calibracion(token=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = requests.get(
            f"{BASE_URL_EYE}/ajustes/",
            headers=headers,
            timeout=10,
        )
        if r.status_code == 401:
            _notify_auth_expired()
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)


def guardar_ajustes_calibracion(esta_calibrado=True, sensibilidad=1.0, token=None):
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = requests.post(
            f"{BASE_URL_EYE}/calibracion/",
            json={
                "esta_calibrado": bool(esta_calibrado),
                "sensibilidad": sensibilidad,
            },
            headers=headers,
            timeout=10,
        )
        if r.status_code == 401:
            _notify_auth_expired()
        payload = _normalize_error_payload(r.status_code, r.json())
        return r.status_code, payload
    except requests.exceptions.RequestException as exc:
        return _network_error_response(exc)