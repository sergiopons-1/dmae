from PyQt6.QtWidgets import (QDialog, QGridLayout, QWidget)
from PyQt6.QtCore import Qt
from shared.widgets.buttons import PrimaryButton
from shared.widgets.fondo import BeigeBg
from shared.widgets.text import TextoInicio
from shared.widgets.imagenes import Imagenes
from shared.widgets.layout import CenterLayout

PRIMARY = "#0E4C66"
BLACK = "#000000"

class InitialWindow(QDialog, BeigeBg):

    def __init__(self, router):
        super().__init__()
        self.router = router
        self.a()

    def a(self):
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        main_layout.setRowStretch(0, 1)
        main_layout.setColumnStretch(0, 1)

        self.imagen = Imagenes(enlace="assets/images/logo.png", ancho=80, alto=80)
        main_layout.addWidget(
            self.imagen,
            0,
            0,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )
        
        center_layout = CenterLayout(espacio=50)


        self.label = TextoInicio(label="¿Tienes cuenta?", tamano=40, upper=True, negrita=True)
        self.iniciar_sesion = PrimaryButton(text="Iniciar sesión", accion=self.inicio_sesion)
        self.registrarse = PrimaryButton(text="Registrarse", accion=self.register)

        center_layout.addWidget(self.label)
        center_layout.addWidget(self.registrarse)
        center_layout.addWidget(self.iniciar_sesion)

        center_widget = QWidget()
        center_widget.setLayout(center_layout)
        main_layout.addWidget(center_widget, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

    def inicio_sesion(self):
        self.router.show_specialist_login()

    def register(self):
        self.router.show_specialist_registration()
