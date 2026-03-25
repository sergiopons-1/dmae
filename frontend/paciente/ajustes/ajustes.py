from PyQt6.QtWidgets import QHBoxLayout, QWidget
from PyQt6.QtCore import Qt
from shared.widgets.sidebar import SidebarPaciente
from shared.widgets.text import TextoInicio, DatosPerfil
from shared.widgets.buttons import PrimaryButton
from shared.widgets.layout import CenterLayout

class Ajustes(QWidget):
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


        center_layout = CenterLayout(espacio=40)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = TextoInicio(label="Ajustes", tamano=22, negrita=True, upper=True)

        center_layout.addWidget(self.label)

        center_widget = QWidget()
        center_widget.setStyleSheet("background-color: #FFF7E7;")
        center_widget.setLayout(center_layout)

        main.addWidget(center_widget)


        