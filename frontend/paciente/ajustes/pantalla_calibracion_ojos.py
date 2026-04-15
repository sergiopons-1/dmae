from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QKeySequence, QPainter, QShortcut
from PyQt6.QtWidgets import QDialog

import cv2
import numpy as np

from eye_tracking.gaze_detector import GazeDetector
from eye_tracking.persistencia_local import guardar_calibration_matrix


class PantallaCalibracionOjos(QDialog):
    def __init__(self, sensibilidad: float, paciente_id=None, parent=None):
        super().__init__(parent)
        self.detector = GazeDetector(ancho_pantalla=1920, alto_pantalla=1080, paciente_id=paciente_id)
        self.detector.establecer_sensibilidad(sensibilidad)

        self._orden = ["sup_izq", "sup_der", "centro", "inf_izq", "inf_der"]
        self._fase = "info"
        self._indice = 0
        self._margen_relativo = 0.10
        self._muestras = {nombre: [] for nombre in self._orden}
        self._buffer_gaze = []
        self._ultimo_gaze = None
        self.calibration_matrix = None

        self.setWindowTitle("Calibración de eye tracking")
        self.setModal(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: white;")

        self.shortcut_espacio = QShortcut(QKeySequence("Space"), self)
        self.shortcut_espacio.setContext(Qt.ShortcutContext.WindowShortcut)
        self.shortcut_espacio.activated.connect(self._on_space_pressed)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def exec(self):
        if not self.detector.iniciar_camara():
            return QDialog.DialogCode.Rejected

        # Recalibrar siempre desde gaze crudo, sin aplicar una matriz previa.
        self.detector.establecer_matriz_calibracion(None)

        self._fase = "info"
        self._indice = 0
        self._muestras = {nombre: [] for nombre in self._orden}
        self._buffer_gaze.clear()
        self._ultimo_gaze = None
        self.calibration_matrix = None
        self.timer.start(30)
        self.showFullScreen()
        self.update()
        return super().exec()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(self.rect(), QColor("white"))

        if self._fase == "info":
            self._dibujar_info(painter)
        else:
            self._dibujar_calibracion(painter)

    def _dibujar_info(self, painter: QPainter):
        ancho = self.width()
        alto = self.height()

        painter.setPen(QColor("#111111"))
        font_texto = QFont("Segoe UI", max(18, alto // 34))
        painter.setFont(font_texto)
        rect_texto = self.rect().adjusted(int(ancho * 0.12), int(alto * 0.16), int(-ancho * 0.12), int(-alto * 0.42))
        texto = (
            "Con esta calibración, el sistema aprenderá cómo se mueven tus ojos y tu cabeza "
            "para ofrecerte una experiencia más fluida."
        )
        painter.drawText(rect_texto, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, texto)

        painter.setPen(QColor("#0E4C66"))
        font_titulo = QFont("Segoe UI", max(24, alto // 22), QFont.Weight.Bold)
        painter.setFont(font_titulo)
        painter.drawText(
            self.rect().adjusted(0, int(alto * 0.42), 0, int(-alto * 0.26)),
            Qt.AlignmentFlag.AlignCenter,
            "Mira los puntos y presiona ESPACIO."
        )

        painter.setPen(QColor("#0E4C66"))
        font_sub = QFont("Segoe UI", max(16, alto // 42))
        painter.setFont(font_sub)
        painter.drawText(
            self.rect().adjusted(0, int(alto * 0.55), 0, int(-alto * 0.18)),
            Qt.AlignmentFlag.AlignCenter,
            "Acompaña la mirada con un leve movimiento de cabeza."
        )

    def _dibujar_calibracion(self, painter: QPainter):
        ancho = self.width()
        alto = self.height()
        puntos = self._obtener_puntos_normales()

        if not self._orden:
            return

        indice_actual = max(0, min(self._indice, len(self._orden) - 1))
        nombre_actual = self._orden[indice_actual]
        x_norm, y_norm = puntos[nombre_actual]
        x = int(x_norm * ancho)
        y = int(y_norm * alto)

        painter.setPen(QColor("#0E4C66"))
        font_titulo = QFont("Segoe UI", max(20, alto // 24), QFont.Weight.Bold)
        painter.setFont(font_titulo)
        painter.drawText(
            self.rect().adjusted(0, int(alto * 0.03), 0, int(-alto * 0.90)),
            Qt.AlignmentFlag.AlignCenter,
            "Mueve suavemente la cabeza hacia el punto."
        )

        painter.setPen(QColor("#0E4C66"))
        font_progreso = QFont("Segoe UI", max(14, alto // 48))
        painter.setFont(font_progreso)
        painter.drawText(
            self.rect().adjusted(0, int(alto * 0.09), 0, int(-alto * 0.84)),
            Qt.AlignmentFlag.AlignCenter,
            f"Punto {indice_actual + 1} de 5 - presiona ESPACIO para registrar"
        )

        # Dibujar puntos de referencia
        for indice, nombre in enumerate(self._orden):
            px_norm, py_norm = puntos[nombre]
            px = int(px_norm * ancho)
            py = int(py_norm * alto)

            if indice == indice_actual:
                painter.setBrush(QColor("#ff1515"))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(px - 14, py - 14, 28, 28)
            else:
                painter.setBrush(QColor("#C8C8C8"))
                painter.setPen(QColor("#FFFFFF"))
                painter.drawEllipse(px - 10, py - 10, 20, 20)

        # resaltar actual con borde
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QColor("#B00000"))
        painter.drawEllipse(x - 22, y - 22, 44, 44)

        if self._ultimo_gaze is not None:
            gx = int(self._ultimo_gaze[0] * ancho)
            gy = int(self._ultimo_gaze[1] * alto)
            painter.setBrush(QColor(0, 180, 0, 180))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(gx - 8, gy - 8, 16, 16)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self._on_space_pressed()
            return
        super().keyPressEvent(event)

    def _tick(self):
        frame = self.detector.obtener_frame()
        if frame is not None:
            gaze = self.detector.detectar_gaze(frame)
            if gaze is not None and gaze.confianza > 0.2:
                self._ultimo_gaze = (float(gaze.x), float(gaze.y))
                self._buffer_gaze.append(self._ultimo_gaze)
                if len(self._buffer_gaze) > 12:
                    self._buffer_gaze = self._buffer_gaze[-12:]

        self.update()

    def _on_space_pressed(self):
        if self._fase == "info":
            self._fase = "calibracion"
            self._indice = 0
            self._buffer_gaze.clear()
            self.update()
            return

        if self._fase != "calibracion":
            return

        if self._indice < 0 or self._indice >= len(self._orden):
            return

        muestra = self._capturar_muestra_actual()
        punto_actual = self._orden[self._indice]
        self._muestras[punto_actual].append(muestra)

        self._indice += 1
        if self._indice >= len(self._orden):
            if self._construir_matriz_calibracion():
                self.timer.stop()
                self.detector.cerrar()

                if self.calibration_matrix is not None:
                    guardar_calibration_matrix(self.calibration_matrix, paciente_id=self.detector.paciente_id)

                self.showNormal()
                self.accept()
                return

            self._indice = 0
            self._muestras = {nombre: [] for nombre in self._orden}
            self._buffer_gaze.clear()
            self._ultimo_gaze = None

        self.update()

    def _capturar_muestra_actual(self):
        if self._buffer_gaze:
            datos = np.array(self._buffer_gaze, dtype=np.float32)
            promedio = np.mean(datos, axis=0)
            self._buffer_gaze.clear()
            return float(promedio[0]), float(promedio[1])

        if self._ultimo_gaze is not None:
            return self._ultimo_gaze

        if self._indice < 0 or self._indice >= len(self._orden):
            return 0.5, 0.5

        return self._obtener_puntos_normales()[self._orden[self._indice]]

    def _obtener_puntos_normales(self):
        margen = self._margen_relativo
        return {
            "sup_izq": (margen, margen),
            "sup_der": (1.0 - margen, margen),
            "centro": (0.50, 0.50),
            "inf_izq": (margen, 1.0 - margen),
            "inf_der": (1.0 - margen, 1.0 - margen),
        }

    def _construir_matriz_calibracion(self) -> bool:
        src_points = []
        dst_points = []
        puntos_normales = self._obtener_puntos_normales()

        for nombre in self._orden:
            muestras = self._muestras.get(nombre, [])
            if len(muestras) < 1:
                return False

            promedio = np.mean(np.array(muestras, dtype=np.float32), axis=0)
            src_points.append([float(promedio[0]), float(promedio[1])])

            x_norm, y_norm = puntos_normales[nombre]
            dst_points.append([float(x_norm), float(y_norm)])

        src = np.array(src_points, dtype=np.float32)
        dst = np.array(dst_points, dtype=np.float32)

        matrix, _ = cv2.estimateAffine2D(src, dst)
        if matrix is None or matrix.shape != (2, 3):
            return False

        self.calibration_matrix = matrix.astype(np.float32)
        self.detector.establecer_matriz_calibracion(self.calibration_matrix)
        return True

    def closeEvent(self, event):
        self.timer.stop()
        self.detector.cerrar()
        super().closeEvent(event)
