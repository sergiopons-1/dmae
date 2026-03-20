from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QDialog)
from PyQt6.QtCore import Qt
from shared.widgets.buttons import PrimaryButton
from shared.widgets.layout import CenterLayout
from shared.widgets.especialista.sidebar import Sidebar
from shared.widgets.text import TextoInicio, FormField

class RegistrarPaciente(QDialog):
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


        center_layout = CenterLayout(espacio=40)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = TextoInicio(label="Nuevo paciente", tamano=22, negrita=True, upper=True)
        self.DNI = FormField(label="DNI:", placeholder="12345678Z", tamano=15)
        self.nombre = FormField(label="Nombre:", placeholder="Nombre", tamano=15)
        self.apellidos = FormField(label="Apellidos:", placeholder="Apellidos", tamano=15)
        self.fechaNacimiento = FormField(label="Fecha de nacimiento:", placeholder="DD/MM/AAAA", tamano=15)
        self.correo = FormField(label="Correo electrónico:", placeholder="example@example.com", tamano=15)
        self.cambiar_contrasena = PrimaryButton(text="GENERAR CÓDIGO", tamano=15, accion=self.generar_codigo)
        

        center_layout.addWidget(self.label)
        center_layout.addWidget(self.DNI)
        center_layout.addWidget(self.nombre)
        center_layout.addWidget(self.apellidos)
        center_layout.addWidget(self.fechaNacimiento)
        center_layout.addWidget(self.correo)
        center_layout.addWidget(self.cambiar_contrasena)

        center_widget = QWidget()
        center_widget.setStyleSheet("background-color: #FFF7E7;")
        center_widget.setLayout(center_layout)
        main.addWidget(center_widget)

    def set_nombre_especialista(self, nombre: str):
        self.nombre_especialista = (nombre or "Especialista").strip() or "Especialista"
        self.sidebar.set_nombre(self.nombre_especialista)

    def generar_codigo(self):
        self.router.show_generar_codigo()