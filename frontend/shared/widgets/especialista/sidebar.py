from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QGuiApplication
from shared.widgets.imagenes import Imagenes
from shared.widgets.buttons import SidebarButton
from shared.widgets.text import TextoInicio

SIDEBAR_BG = "#0E4C66"
SIDEBAR_TEXT = "#FFFFFF"
SEPARATOR_COLOR = "#FFF7E7"


class Sidebar(QWidget):
    go_perfil = pyqtSignal()
    go_pacientes = pyqtSignal()
    go_logout = pyqtSignal()

    def __init__(self, nombre: str = "Especialista", parent=None, router=None):
        super().__init__(parent)
        self.nombre = nombre
        self.router = router
        if self.router is None and parent is not None and hasattr(parent, "router"):
            self.router = parent.router

        ancho_sidebar = self._calcular_ancho_sidebar()
        self.setFixedWidth(ancho_sidebar)  # mismo ancho en todos los apartados
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(f"background-color: {SIDEBAR_BG};")

        self._build_ui()

    def _calcular_ancho_sidebar(self) -> int:
        # 16% del ancho de pantalla, acotado para mantener diseño
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return 280

        ancho_pantalla = screen.availableGeometry().width()
        ancho = int(ancho_pantalla * 0.16)
        return max(250, min(340, ancho))

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        layout.addWidget(self._build_header())
        
        layout.addWidget(self._separator())
        
        layout.addWidget(self._nav_button("Mi perfil", self.perfil))
        layout.addWidget(self._separator())
        layout.addWidget(self._nav_button("Pacientes", self.pacientes))
        layout.addWidget(self._separator())

        
        spacer = QWidget()
        spacer.setStyleSheet(f"background-color: {SIDEBAR_BG};")  # ← azul, no beige
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(spacer)

        
        layout.addWidget(self._separator())
        layout.addWidget(self._nav_button("Cerrar sesión", self.cerrar_sesion))


    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(QColor("#1878A1"))  
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        painter.end()

   
    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setStyleSheet(f"background-color: {SIDEBAR_BG};")

        col = QVBoxLayout(header)
        col.setContentsMargins(16, 32, 16, 20)
        col.setSpacing(10)
        col.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        
        foto = Imagenes(enlace="assets/images/foto_especialista.png", ancho=80, alto=80)
        foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col.addWidget(foto, alignment=Qt.AlignmentFlag.AlignHCenter)

        
        nombre_lbl = TextoInicio(label = self.nombre, tamano=13, color=SIDEBAR_TEXT, negrita=True)
        col.addWidget(nombre_lbl)

        return header

    

    def _nav_button(self, texto: str, señal: pyqtSignal) -> QWidget:
        btn = SidebarButton(text=texto, tamano=13)
        btn.setMinimumHeight(52)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(señal)
        return btn

    def cerrar_sesion(self):
        self.go_logout.emit()
        if self.router is not None and hasattr(self.router, "show_inicio"):
            self.router.show_inicio()

    def pacientes(self):
        self.go_pacientes.emit()
        if self.router is not None and hasattr(self.router, "show_pacientes_especialista"):
            self.router.show_pacientes_especialista()

    def perfil(self):
        self.go_perfil.emit()
        if self.router is not None and hasattr(self.router, "show_perfil_especialista"):
            self.router.show_perfil_especialista()

    def _separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {SEPARATOR_COLOR}; border: none;")
        return sep