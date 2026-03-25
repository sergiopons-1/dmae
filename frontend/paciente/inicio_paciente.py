from shared.widgets.sidebar import SidebarPaciente
from PyQt6.QtWidgets import QHBoxLayout, QWidget
from PyQt6.QtGui import QPainter, QPixmap, QColor
from PyQt6.QtCore import Qt

class InicioPaciente(QWidget):
    def __init__(self, router, nombre=""):
        super().__init__()
        self.router = router
        self.nombre_paciente = nombre

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        self.sidebar = SidebarPaciente(nombre=nombre, parent=self)
        self.sidebar.go_logout.connect(self.router.show_inicio)
        main.addWidget(self.sidebar)

        self.contenido = FondoConOverlay("assets/images/foto_pueblo.png")
        main.addWidget(self.contenido, stretch=1)

    def set_nombre_paciente(self, nombre: str):
        self.nombre_paciente = (nombre or "Paciente").strip() or "Paciente"
        self.sidebar.set_nombre(self.nombre_paciente)

class FondoConOverlay(QWidget):
    def __init__(self, ruta_imagen: str, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap(ruta_imagen)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        if not self._pixmap.isNull():
            fondo = self._pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(self.rect(), fondo)
        else:
            painter.fillRect(self.rect(), QColor("#FFF7E7"))

        painter.fillRect(self.rect(), QColor(255, 247, 231, 102))