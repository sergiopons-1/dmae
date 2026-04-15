import threading
import time

from PyQt6.QtWidgets import QApplication

import numpy as np
from pynput.mouse import Button, Controller as MouseController

from eye_tracking.gaze_detector import GazeDetector
class EyeTrackingController:
    """
    Controlador de eye tracking que mapea la mirada al cursor del ratón.
    Se activa cuando comienza una rehabilitación y se desactiva al terminar.
    """
    
    def __init__(self, sensibilidad: float = 1.0, paciente_id=None, ancho_pantalla=1920, alto_pantalla=1080):
        self.detector = GazeDetector(
            ancho_pantalla=ancho_pantalla,
            alto_pantalla=alto_pantalla,
            paciente_id=paciente_id
        )
        self.detector.establecer_sensibilidad(sensibilidad)
        self.mouse_controller = MouseController()
        
        self._activo = False
        self._buffer_gaze = []
        self._buffer_size = 5
        self._ultimo_gaze = None
        self.paciente_id = paciente_id
        
        self._tracking_thread = None
        self._widget_area = None
        self._boca_abierta_previa = False
        self._ultimo_click = 0.0
        self._debounce_click_segundos = 0.5
        
    def iniciar(self, widget_area=None) -> bool:
        """
        Inicia el control del eye tracking.
        
        Args:
            widget_area: Widget opcional que limita el área de control del ratón
            
        Returns:
            True si se inició correctamente, False en caso contrario
        """
        if not self.detector.iniciar_camara():
            return False
        
        self._widget_area = widget_area
        self._activo = True
        self._buffer_gaze.clear()
        self._boca_abierta_previa = False
        self._ultimo_click = 0.0
        
        self._tracking_thread = threading.Thread(target=self._loop_tracking, daemon=True)
        self._tracking_thread.start()
        
        return True
    
    def detener(self):
        """Detiene el control del eye tracking."""
        self._activo = False
        
        if self._tracking_thread is not None and self._tracking_thread.is_alive():
            self._tracking_thread.join(timeout=1.0)
        self._tracking_thread = None
        
        self.detector.cerrar()
    
    def _loop_tracking(self):
        """Bucle de tracking en hilo independiente para no bloquear la UI."""
        while self._activo:
            frame = self.detector.obtener_frame()
            if frame is None:
                time.sleep(0.03)
                continue

            gaze = self.detector.detectar_gaze(frame)
            if gaze is not None and gaze.confianza > 0.2:
                gaze_point = (float(gaze.x), float(gaze.y))
                self._buffer_gaze.append(gaze_point)
                if len(self._buffer_gaze) > self._buffer_size:
                    self._buffer_gaze.pop(0)

                promedio = np.mean(np.array(self._buffer_gaze), axis=0)
                self._ultimo_gaze = (float(promedio[0]), float(promedio[1]))

                screen = QApplication.primaryScreen()
                if screen is not None:
                    screen_geometry = screen.geometry()
                    pantalla_ancho = screen_geometry.width()
                    pantalla_alto = screen_geometry.height()

                    x_pixel = int(self._ultimo_gaze[0] * pantalla_ancho)
                    y_pixel = int(self._ultimo_gaze[1] * pantalla_alto)

                    x_pixel = max(0, min(x_pixel, pantalla_ancho - 1))
                    y_pixel = max(0, min(y_pixel, pantalla_alto - 1))

                    self.mouse_controller.position = (x_pixel, y_pixel)

            boca_abierta = self.detector.detectar_boca_abierta(frame)
            if boca_abierta and not self._boca_abierta_previa:
                ahora = time.time()
                if (ahora - self._ultimo_click) >= self._debounce_click_segundos:
                    self.mouse_controller.click(Button.left, 1)
                    self._ultimo_click = ahora
            self._boca_abierta_previa = boca_abierta

            time.sleep(0.016)
    
    def get_ultimo_gaze(self):
        """Retorna el último punto de mirada en coordenadas normalizadas (0-1)."""
        return self._ultimo_gaze
    
    def is_activo(self):
        """Retorna si el eye tracking está activo."""
        return self._activo
