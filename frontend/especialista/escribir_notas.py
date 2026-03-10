from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QDialog)
from PyQt6.QtCore import Qt
from shared.widgets.buttons import PrimaryButton
from shared.widgets.layout import CenterLayout
from shared.widgets.especialista.sidebar import Sidebar
from shared.widgets.text import TextoInicio, FormField

class PublicarNota(QDialog):
    def __init__(self, router, nombre="Carlos Mateo"):
        super().__init__()
        self.router = router

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        self.sidebar = Sidebar(nombre=nombre, parent=self)
        self.sidebar.go_logout.connect(self.router.show_inicio)
        main.addWidget(self.sidebar)


        center_layout = CenterLayout(espacio=40)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = TextoInicio(label="Añadir nota", tamano=15, negrita=True, upper=True)
        self.titulo_nota = TextoInicio(label="Nueva nota para " + nombre, tamano=12, negrita=True)
        self.cambiar_contrasena = PrimaryButton(text="PUBLICAR NOTA", tamano=13, accion=self.publicar_nota)
        

        center_layout.addWidget(self.label)
        center_layout.addWidget(self.titulo_nota)
        center_layout.addWidget(self.cambiar_contrasena)

        center_widget = QWidget()
        center_widget.setStyleSheet("background-color: #FFF7E7;")
        center_widget.setLayout(center_layout)
        main.addWidget(center_widget)


    def publicar_nota(self):
        self.router.show_progreso_individual()