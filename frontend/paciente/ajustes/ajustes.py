from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QImage, QKeySequence, QPainter, QPixmap, QShortcut
from PyQt6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

import cv2
import numpy as np

from api_cliente import guardar_ajustes_calibracion, obtener_ajustes_calibracion
from eye_tracking.gaze_detector import GazeDetector
from eye_tracking.persistencia_local import (
    cargar_user_settings,
    guardar_calibration_matrix,
    guardar_user_settings,
)
from paciente.ajustes.pantalla_calibracion_ojos import PantallaCalibracionOjos
from shared.widgets.buttons import PrimaryButton
from shared.widgets.layout import CenterLayout
from shared.widgets.sidebar import SidebarPaciente
from shared.widgets.text import TextoInicio


class VentanaCalibracion(QDialog):
    def __init__(self, sensibilidad: float, parent=None):
        super().__init__(parent)
        router = getattr(parent, "router", None)
        paciente_id = getattr(router, "paciente_id", None)
        self.detector = GazeDetector(ancho_pantalla=1920, alto_pantalla=1080, paciente_id=paciente_id)
        self.detector.establecer_sensibilidad(sensibilidad)

        self._orden = ["sup_izq", "sup_der", "centro", "inf_izq", "inf_der"]
        self._margen_relativo = 0.10

        self._fase = "info"
        self._indice = 0
        self._muestras = {nombre: [] for nombre in self._orden}
        self._buffer_gaze = []
        self._ultimo_gaze = None
        self.calibration_matrix = None

        self.setWindowTitle("Calibración de eye tracking")
        self.setModal(True)
        self.setWindowState(self.windowState() | Qt.WindowState.WindowFullScreen)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label_estado = QLabel(
            "Con esta calibración, el sistema aprenderá cómo se mueven tus ojos y tu cabeza para ofrecerte una experiencia más fluida."
        )
        self.label_estado.setWordWrap(True)
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_estado.setFont(QFont("Segoe UI", 16))
        self.label_estado.setStyleSheet("color: #0E4C66;")

        self.label_indicacion = QLabel("Mira los puntos y presiona ESPACIO.")
        self.label_indicacion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_indicacion.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.label_indicacion.setStyleSheet("color: #0E4C66;")

        self.label_sub = QLabel("Acompaña la mirada con un leve movimiento de cabeza.")
        self.label_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_sub.setFont(QFont("Segoe UI", 15))
        self.label_sub.setStyleSheet("color: #0E4C66;")

        self.label_progreso = QLabel("")
        self.label_progreso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_progreso.setFont(QFont("Segoe UI", 13))
        self.label_progreso.setStyleSheet("color: #0E4C66;")
        self.label_video = QLabel()
        self.label_video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.label_video.setStyleSheet("background-color: #ECECEC; border: 0px;")

        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(40, 18, 40, 12)
        header_layout.setSpacing(8)
        header_layout.addWidget(self.label_estado)
        header_layout.addWidget(self.label_indicacion)
        header_layout.addWidget(self.label_sub)
        header_layout.addWidget(self.label_progreso)

        layout.addWidget(header)
        layout.addWidget(self.label_video, 1)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.shortcut_espacio = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self.shortcut_espacio.setContext(Qt.ShortcutContext.WindowShortcut)
        self.shortcut_espacio.activated.connect(self._on_space_pressed)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

        self._render_info()

    def exec(self):
        if not self.detector.iniciar_camara():
            self.label_estado.setText("No se pudo abrir la cámara")
            return QDialog.DialogCode.Rejected

        self._fase = "info"
        self._indice = 0
        self._buffer_gaze.clear()
        self._ultimo_gaze = None
        self.timer.start(30)
        self._render_info()
        self.showFullScreen()
        return super().exec()

    def _tick(self):
        frame = self.detector.obtener_frame()
        if frame is None:
            return

        gaze = self.detector.detectar_gaze(frame)
        if gaze is not None and gaze.confianza > 0.2:
            self._ultimo_gaze = (float(gaze.x), float(gaze.y))
            self._buffer_gaze.append(self._ultimo_gaze)
            if len(self._buffer_gaze) > 12:
                self._buffer_gaze = self._buffer_gaze[-12:]

        if self._fase == "calibracion":
            self._render_punto_actual()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self._on_space_pressed()
            return
        super().keyPressEvent(event)

    def _on_space_pressed(self):
        if not self.isVisible():
            return

        if self._fase == "info":
            self._fase = "calibracion"
            self._indice = 0
            self.label_estado.setText("Mira el punto y presiona ESPACIO")
            self.label_indicacion.setText("Mueve suavemente la cabeza hacia el punto.")
            self.label_sub.setText("")
            self.label_progreso.setText("Punto 1 de 5")
            self._render_punto_actual()
            return

        if self._fase != "calibracion":
            return

        muestra = self._capturar_muestra_actual()
        punto_actual = self._orden[self._indice]
        self._muestras[punto_actual].append(muestra)

        self._indice += 1
        if self._indice >= len(self._orden):
            frame_w = self.label_video.width()
            frame_h = self.label_video.height()
            if self._construir_matriz_calibracion(frame_w, frame_h):
                self.timer.stop()
                self.detector.cerrar()
                self.accept()
                return

            self.label_progreso.setText("Error al construir la matriz. Repite calibración.")
            self._indice = 0
            self._muestras = {nombre: [] for nombre in self._orden}
            self._render_punto_actual()
            return

        self.label_progreso.setText(f"Punto {self._indice + 1} de 5")
        self._render_punto_actual()

    def _capturar_muestra_actual(self):
        if self._buffer_gaze:
            datos = np.array(self._buffer_gaze, dtype=np.float32)
            promedio = np.mean(datos, axis=0)
            self._buffer_gaze.clear()
            return float(promedio[0]), float(promedio[1])

        if self._ultimo_gaze is not None:
            return self._ultimo_gaze

        # Fallback: registra el punto objetivo para no bloquear el flujo al pulsar ESPACIO.
        nombre = self._orden[self._indice]
        return self._obtener_puntos_normales()[nombre]

    def _render_info(self):
        pixmap = QPixmap(self.label_video.size())
        pixmap.fill(QColor("#ECECEC"))
        self.label_video.setPixmap(pixmap)

    def _render_punto_actual(self):
        pixmap = QPixmap(self.label_video.size())
        pixmap.fill(QColor("#ECECEC"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#ff1515"))

        nombre = self._orden[self._indice]
        x_norm, y_norm = self._obtener_puntos_normales()[nombre]
        x = int(x_norm * pixmap.width())
        y = int(y_norm * pixmap.height())
        painter.drawEllipse(x - 12, y - 12, 24, 24)
        painter.end()

        self.label_video.setPixmap(pixmap)

    def _obtener_puntos_normales(self):
        margen = self._margen_relativo
        return {
            "sup_izq": (margen, margen),
            "sup_der": (1.0 - margen, margen),
            "centro": (0.50, 0.50),
            "inf_izq": (margen, 1.0 - margen),
            "inf_der": (1.0 - margen, 1.0 - margen),
        }

    def _construir_matriz_calibracion(self, frame_w: int, frame_h: int) -> bool:
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


class Ajustes(QWidget):
    def __init__(self, router, nombre=""):
        super().__init__()
        self.router = router
        self.nombre_paciente = nombre
        self.paciente_id = getattr(router, "paciente_id", None)

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        self.sidebar = SidebarPaciente(nombre=nombre, parent=self)
        self.sidebar.go_logout.connect(self.router.show_inicio)
        main.addWidget(self.sidebar)

        center_layout = CenterLayout(espacio=40)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = TextoInicio(label="Ajustes", tamano=22, negrita=True, upper=True)
        self.estado = TextoInicio(label="Estado: sin calibrar", tamano=14, negrita=True)
        self.mensaje = TextoInicio(label="Pulsa en iniciar calibración para abrir la ventana de calibración", tamano=12)

        self.selector_sensibilidad = QComboBox()
        self.selector_sensibilidad.addItem("Baja (0.8)", 0.8)
        self.selector_sensibilidad.addItem("Normal (1.0)", 1.0)
        self.selector_sensibilidad.addItem("Alta (1.2)", 1.2)
        self.selector_sensibilidad.addItem("Muy alta (1.5)", 1.5)
        self.selector_sensibilidad.setCurrentIndex(1)
        self.selector_sensibilidad.setFixedWidth(240)
        self.selector_sensibilidad.setStyleSheet("""
            QComboBox {
                color: #0E4C66;
                background-color: white;
                border: 1px solid #0E4C66;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                color: #0E4C66;
                background-color: white;
                selection-background-color: #0E4C66;
                selection-color: white;
            }
        """)

        self.btn_iniciar = PrimaryButton(text="Iniciar calibración", tamano=12, accion=self.iniciar_calibracion)

        center_layout.addWidget(self.label)
        center_layout.addWidget(self.estado)
        center_layout.addWidget(TextoInicio(label="Sensibilidad de mirada", tamano=12, negrita=True))
        center_layout.addWidget(self.selector_sensibilidad)
        center_layout.addWidget(self.mensaje)
        center_layout.addWidget(self.btn_iniciar)

        center_widget = QWidget()
        center_widget.setStyleSheet("background-color: #FFF7E7;")
        center_widget.setLayout(center_layout)
        main.addWidget(center_widget)

        self._cargar_ajustes_locales()

    def _cargar_ajustes_locales(self):
        paciente_id = getattr(self.router, "paciente_id", None)
        settings = cargar_user_settings(paciente_id)
        sensibilidad = float(settings.get("sensibilidad", 1.0) or 1.0)

        for indice in range(self.selector_sensibilidad.count()):
            val = float(self.selector_sensibilidad.itemData(indice) or 1.0)
            if abs(val - sensibilidad) < 0.001:
                self.selector_sensibilidad.setCurrentIndex(indice)
                break



    def iniciar_calibracion(self):
        paciente_id = getattr(self.router, "paciente_id", None)
        sensibilidad = float(self.selector_sensibilidad.currentData() or 1.0)
        ventana = PantallaCalibracionOjos(sensibilidad, paciente_id=getattr(self.router, "paciente_id", None), parent=self)
        resultado = ventana.exec()

        if resultado != QDialog.DialogCode.Accepted or ventana.calibration_matrix is None:
            self.mensaje.setText("Calibración no completada")
            return

        # Persistencia local (modelo 7.2)
        guardar_calibration_matrix(ventana.calibration_matrix, paciente_id=paciente_id)
        guardar_user_settings(sensibilidad=sensibilidad, paciente_id=paciente_id)


        # Persistencia remota actual del sistema
        token = getattr(self.router, "auth_token", None)
        if token:
            status_code, data = guardar_ajustes_calibracion(
                esta_calibrado=True,
                sensibilidad=sensibilidad,
                token=token,
            )
            if status_code != 200 and isinstance(data, dict):
                self.mensaje.setText(data.get("error", "Calibración local guardada, pero hubo un error en servidor"))
                return

        self.estado.setText(f"Estado: calibrado (sensibilidad {sensibilidad:.1f})")
        self.mensaje.setText("Calibración guardada (local y servidor)")

    def showEvent(self, event):
        super().showEvent(event)
        self._cargar_ajustes_actuales_backend()

    def _cargar_ajustes_actuales_backend(self):
        token = getattr(self.router, "auth_token", None)
        if not token:
            return

        status_code, data = obtener_ajustes_calibracion(token)
        if status_code != 200 or not isinstance(data, dict):
            return

        sensibilidad = float(data.get("sensibilidad", 1.0) or 1.0)
        esta_calibrado = bool(data.get("esta_calibrado", False))

        for indice in range(self.selector_sensibilidad.count()):
            val = float(self.selector_sensibilidad.itemData(indice) or 1.0)
            if abs(val - sensibilidad) < 0.001:
                self.selector_sensibilidad.setCurrentIndex(indice)
                break

        if esta_calibrado:
            self.estado.setText(f"Estado: calibrado (sensibilidad {sensibilidad:.1f})")
            self.mensaje.setText("Puedes recalibrar cuando quieras")
        else:
            self.estado.setText("Estado: sin calibrar")
            self.mensaje.setText("Pulsa en iniciar calibración para abrir la ventana de calibración")

    def set_nombre_paciente(self, nombre: str):
        self.nombre_paciente = (nombre or "Paciente").strip() or "Paciente"
        self.sidebar.set_nombre(self.nombre_paciente)
