"""
Detección de la mirada usando MediaPipe Face Mesh y OpenCV.
Captura la posición del ojo y la mapea a coordenadas en pantalla.
"""

import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple

from eye_tracking.persistencia_local import cargar_calibration_matrix


@dataclass
class GazePoint:
    """Punto de mirada en coordenadas normalizadas [0, 1]"""
    x: float  # 0 = izquierda, 1 = derecha
    y: float  # 0 = arriba, 1 = abajo
    confianza: float  # 0-1, qué tan confiable es la detección


class GazeDetector:
    """
    Detector de mirada usando MediaPipe Face Mesh.
    Calibración: relación entre puntos iris y posición en pantalla.
    """
    
    def __init__(self, ancho_pantalla: int = 1920, alto_pantalla: int = 1080, paciente_id=None):
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla
        self.paciente_id = paciente_id
        
        # Inicializar MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        
        # Inicializar captura
        self.cap = None
        self._calibracion: dict[str, Tuple[float, float]] = {}  # {nombre_punto: (x_iris, y_iris)}
        self._sensibilidad = 1.0
        self._matriz_calibracion = cargar_calibration_matrix(paciente_id)
        
        # Puntos de referencia iris (índices en face_mesh landmarks)
        self.IRIS_IZQUIERDO = 468  # Centro iris izquierdo
        self.IRIS_DERECHO = 473   # Centro iris derecho
        self.LABIO_SUPERIOR = 13
        self.LABIO_INFERIOR = 14

    def _amplificar_suave(self, valor: float, ganancia: float = 3.0) -> float:
        """Amplifica alrededor del centro sin salir de [0, 1]."""
        delta = float(valor) - 0.5
        normalizador = np.tanh(0.5 * ganancia)
        if abs(normalizador) < 1e-6:
            return float(valor)
        return 0.5 + 0.5 * (np.tanh(delta * ganancia) / normalizador)
        
    def iniciar_camara(self, camera_id: int = 0) -> bool:
        """Abre la captura de cámara"""
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            print(f"❌ No se pudo abrir la cámara {camera_id}")
            return False
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return True
    
    def cerrar_camara(self):
        """Cierra la cámara"""
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def obtener_frame(self) -> Optional[np.ndarray]:
        """Lee un frame de la cámara"""
        if not self.cap or not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return cv2.flip(frame, 1)  # Espejo horizontal
    
    def detectar_gaze(self, frame: np.ndarray) -> Optional[GazePoint]:
        """
        Detecta la posición del gaze en el frame.
        Retorna posición normalizada [0, 1] en pantalla.
        """
        if frame is None:
            return None
        
        results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks or len(results.multi_face_landmarks) == 0:
            return None
        
        landmarks = results.multi_face_landmarks[0].landmark
        
        # Obtener posición del iris (usar el promedio de ambos ojos para mayor precisión)
        iris_izq = landmarks[self.IRIS_IZQUIERDO]
        iris_der = landmarks[self.IRIS_DERECHO]
        
        # Promedio de ambos iris
        x_norm = (iris_izq.x + iris_der.x) / 2.0
        y_norm = (iris_izq.y + iris_der.y) / 2.0
        # En MediaPipe Face Mesh, z es profundidad relativa, no confianza de deteccion.
        # Si hay landmarks validos, tratamos la lectura como confiable.
        confianza = 1.0
        
        # Amplificacion suave para evitar saturacion en bordes (trayectoria rectangular).
        centro_x, centro_y = 0.5, 0.5
        x_amplificado = self._amplificar_suave(x_norm, ganancia=3.0)
        y_amplificado = self._amplificar_suave(y_norm, ganancia=3.0)

        # Aplicar sensibilidad (escalar respecto al centro)
        x_ajustado = centro_x + (x_amplificado - centro_x) * self._sensibilidad
        y_ajustado = centro_y + (y_amplificado - centro_y) * self._sensibilidad

        # Aplicar matriz de calibración si existe
        if self._matriz_calibracion is not None:
            punto = np.array([[[x_ajustado, y_ajustado]]], dtype=np.float32)
            transformado = cv2.transform(punto, self._matriz_calibracion)
            x_ajustado = float(transformado[0][0][0])
            y_ajustado = float(transformado[0][0][1])
        
        # Clampear a [0, 1]
        x_ajustado = max(0.0, min(1.0, x_ajustado))
        y_ajustado = max(0.0, min(1.0, y_ajustado))
        
        return GazePoint(x=x_ajustado, y=y_ajustado, confianza=confianza)

    def detectar_boca_abierta(self, frame: np.ndarray, umbral: float = 0.02) -> bool:
        """Detecta gesto de boca abierta usando landmarks de labios."""
        if frame is None:
            return False

        results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks or len(results.multi_face_landmarks) == 0:
            return False

        landmarks = results.multi_face_landmarks[0].landmark
        labio_sup = landmarks[self.LABIO_SUPERIOR]
        labio_inf = landmarks[self.LABIO_INFERIOR]

        distancia_boca = abs(labio_inf.y - labio_sup.y)
        return distancia_boca > umbral
    
    def calibrar_punto(self, nombre: str, gaze_point: GazePoint):
        """
        Registra un punto de calibración.
        Durante la calibración, el paciente mira un punto en pantalla.
        """
        self._calibracion[nombre] = (gaze_point.x, gaze_point.y)
    
    def obtener_calibracion(self) -> dict[str, Tuple[float, float]]:
        """Retorna los puntos de calibración guardados"""
        return self._calibracion.copy()
    
    def limpiar_calibracion(self):
        """Borra la calibración actual"""
        self._calibracion.clear()
    
    def establecer_sensibilidad(self, valor: float):
        """
        Ajusta la sensibilidad del gaze (0.2 a 3.0).
        Valores > 1.0 amplifican el movimiento del ojo.
        Valores < 1.0 reducen el movimiento.
        """
        self._sensibilidad = max(0.2, min(3.0, valor))

    def establecer_matriz_calibracion(self, matriz: np.ndarray | None):
        if matriz is None:
            self._matriz_calibracion = None
            return

        if isinstance(matriz, np.ndarray) and matriz.shape == (2, 3):
            self._matriz_calibracion = matriz.astype(np.float32)

    def recargar_matriz_calibracion(self):
        self._matriz_calibracion = cargar_calibration_matrix(self.paciente_id)
    
    def cerrar(self):
        """Cierra detector y libera recursos"""
        self.cerrar_camara()
        if self.face_mesh:
            self.face_mesh.close()
