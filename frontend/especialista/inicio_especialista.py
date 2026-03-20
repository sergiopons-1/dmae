from shared.widgets.especialista.sidebar import Sidebar
from PyQt6.QtWidgets import QHBoxLayout, QWidget
from PyQt6.QtGui import QPainter, QPixmap, QColor
from PyQt6.QtCore import Qt

class InicioEspecialista(QWidget):
    def __init__(self, router, nombre="Carlos Mateo"):
        super().__init__()
        self.router = router
        self.nombre_especialista = nombre

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        self.sidebar = Sidebar(nombre=nombre, parent=self)
        self.sidebar.go_logout.connect(self.router.show_inicio)
        main.addWidget(self.sidebar)

        self.contenido = FondoConOverlay("assets/images/foto_pueblo.png")
        main.addWidget(self.contenido, stretch=1)

    def set_nombre_especialista(self, nombre: str):
        self.nombre_especialista = (nombre or "Especialista").strip() or "Especialista"
        self.sidebar.set_nombre(self.nombre_especialista)

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