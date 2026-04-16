import threading
import time

from PyQt6.QtWidgets import QApplication

import numpy as np
from pynput.mouse import Button, Controller as MouseController

from eye_tracking.gaze_detector import GazeDetector
class EyeTrackingController:
    def __init__(self, sensibilidad: float = 1.0, paciente_id=None, ancho_pantalla=1920, alto_pantalla=1080):
        self._zona_ancho = 1920
        self._zona_alto = 1080

        self.detector = GazeDetector(
            ancho_pantalla=self._zona_ancho,
            alto_pantalla=self._zona_alto,
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
        self._min_gaze_x = None
        self._max_gaze_x = None
        self._min_gaze_y = None
        self._max_gaze_y = None
        self._span_minimo = 0.08
        self._frames = 0

    def _reset_autocalibracion_rango(self):
        self._min_gaze_x = None
        self._max_gaze_x = None
        self._min_gaze_y = None
        self._max_gaze_y = None
        self._frames = 0

    def _normalizar_gaze_a_pantalla(self, x: float, y: float) -> tuple[float, float]:
        if self._min_gaze_x is None:
            self._min_gaze_x = x
            self._max_gaze_x = x
            self._min_gaze_y = y
            self._max_gaze_y = y
            return x, y

        self._min_gaze_x = min(self._min_gaze_x, x)
        self._max_gaze_x = max(self._max_gaze_x, x)
        self._min_gaze_y = min(self._min_gaze_y, y)
        self._max_gaze_y = max(self._max_gaze_y, y)

        span_x = self._max_gaze_x - self._min_gaze_x
        span_y = self._max_gaze_y - self._min_gaze_y

        if span_x < self._span_minimo or span_y < self._span_minimo:
            return x, y

        x_norm = (x - self._min_gaze_x) / max(span_x, 1e-6)
        y_norm = (y - self._min_gaze_y) / max(span_y, 1e-6)
        return x_norm, y_norm
        
    def iniciar(self, widget_area=None) -> bool:
        
        if not self.detector.iniciar_camara():
            return False
        
        self._widget_area = widget_area
        self._activo = True
        self._buffer_gaze.clear()
        self._reset_autocalibracion_rango()
        self._boca_abierta_previa = False
        self._ultimo_click = 0.0

        print(
            f"[EyeTracking] Iniciando con zona fija {self._zona_ancho}x{self._zona_alto} "
            f"(detector {self.detector.ancho_pantalla}x{self.detector.alto_pantalla})"
        )
        
        self._tracking_thread = threading.Thread(target=self._loop_tracking, daemon=True)
        self._tracking_thread.start()
        
        return True
    
    def detener(self):
        self._activo = False
        
        if self._tracking_thread is not None and self._tracking_thread.is_alive():
            self._tracking_thread.join(timeout=1.0)
        self._tracking_thread = None
        
        self.detector.cerrar()
    
    def _loop_tracking(self):
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
                x_norm, y_norm = self._normalizar_gaze_a_pantalla(
                    self._ultimo_gaze[0], self._ultimo_gaze[1]
                )
                self._frames += 1

                pantalla_ancho = self._zona_ancho
                pantalla_alto = self._zona_alto

                x_pixel = int(x_norm * pantalla_ancho)
                y_pixel = int(y_norm * pantalla_alto)

                x_pixel = max(0, min(x_pixel, pantalla_ancho - 1))
                y_pixel = max(0, min(y_pixel, pantalla_alto - 1))

                self.mouse_controller.position = (x_pixel, y_pixel)

                if self._frames % 120 == 0:
                    span_x = (self._max_gaze_x - self._min_gaze_x) if self._max_gaze_x is not None else 0.0
                    span_y = (self._max_gaze_y - self._min_gaze_y) if self._max_gaze_y is not None else 0.0
                    print(
                        f"[EyeTracking] rango gaze x=[{self._min_gaze_x:.3f},{self._max_gaze_x:.3f}] span_x={span_x:.3f} "
                        f"y=[{self._min_gaze_y:.3f},{self._max_gaze_y:.3f}] span_y={span_y:.3f}"
                    )

            boca_abierta = self.detector.detectar_boca_abierta(frame)
            if boca_abierta and not self._boca_abierta_previa:
                ahora = time.time()
                if (ahora - self._ultimo_click) >= self._debounce_click_segundos:
                    self.mouse_controller.click(Button.left, 1)
                    self._ultimo_click = ahora
            self._boca_abierta_previa = boca_abierta

            time.sleep(0.016)
    
    def get_ultimo_gaze(self):
        return self._ultimo_gaze
    
    def is_activo(self):
        return self._activo
