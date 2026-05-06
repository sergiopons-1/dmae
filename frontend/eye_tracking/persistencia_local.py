import json
from pathlib import Path

import numpy as np


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "eye_tracking" / "data"
GLOBAL_DIR = DATA_DIR / "global"
DEFAULT_PATIENT_ID = "global"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _patient_dir(paciente_id=None) -> Path:
    _ensure_data_dir()
    patient_key = str(paciente_id) if paciente_id not in (None, "") else DEFAULT_PATIENT_ID
    patient_dir = DATA_DIR / f"paciente_{patient_key}"
    patient_dir.mkdir(parents=True, exist_ok=True)
    return patient_dir


def _user_settings_path(paciente_id=None) -> Path:
    return _patient_dir(paciente_id) / "user_settings.json"


def _calibration_matrix_path(paciente_id=None) -> Path:
    return _patient_dir(paciente_id) / "calibration_matrix.npy"


def _read_json(path: Path, default: dict) -> dict:
    _ensure_data_dir()
    if not path.exists():
        return default.copy()

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else default.copy()
    except (json.JSONDecodeError, OSError):
        return default.copy()


def _write_json(path: Path, payload: dict) -> None:
    _ensure_data_dir()
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def cargar_user_settings(paciente_id=None) -> dict:
    return _read_json(
        _user_settings_path(paciente_id),
        {
            "paciente_id": paciente_id,
            "sensibilidad": 1.0,
            "gesto_clic": "abrir_boca",
            "gesto_doble_clic": None,
        },
    )


def guardar_user_settings(sensibilidad: float, paciente_id=None) -> None:
    payload = {
        "paciente_id": paciente_id,
        "sensibilidad": float(sensibilidad),
        "gesto_clic": "abrir_boca",
        "gesto_doble_clic": None,
    }
    _write_json(_user_settings_path(paciente_id), payload)


def guardar_calibration_matrix(matrix: np.ndarray, paciente_id=None) -> None:
    _ensure_data_dir()
    np.save(_calibration_matrix_path(paciente_id), matrix)


def cargar_calibration_matrix(paciente_id=None) -> np.ndarray | None:
    _ensure_data_dir()
    calibration_path = _calibration_matrix_path(paciente_id)
    if not calibration_path.exists():
        return None

    try:
        matrix = np.load(calibration_path)
    except OSError:
        return None

    if isinstance(matrix, np.ndarray) and matrix.shape == (2, 3):
        return matrix
    return None
