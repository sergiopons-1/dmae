from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from shared.widgets.buttons import PrimaryButton
from shared.widgets.fondo import BeigeBg
from especialista.widgets.card import Card
from shared.widgets.text import FormField, TextoInicio
from shared.widgets.imagenes import Imagenes
from shared.widgets.layout import MainLayout, CenterLayout


PRIMARY = "#0E4C66"
BLACK = "#000000"

class CambiarContraseña(QDialog, BeigeBg):

    def __init__(self, router):
        super().__init__()
        self.router = router
        self.nombre_especialista = "Especialista"
        self.a()

    def a(self):
        main_layout = MainLayout()
        self.setLayout(main_layout)

        self.imagen = Imagenes(enlace="assets/images/logo.png", ancho=80, alto=80)
        main_layout.addWidget(self.imagen)
       
        center_layout = CenterLayout(espacio=40)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.texto1 = TextoInicio(label="Hola nombre", tamano=24, upper=True, negrita=True)
        self.texto2 = TextoInicio(label="Cambia tu contraseña", tamano=24, upper=True, negrita=True)
        self.contraseña = FormField(label="Contraseña", tamano=14, password=True)
        self.repetir_contraseña = FormField(label="Repetir contraseña", tamano=14, password=True)
        self.cambiar_contrasena = PrimaryButton(text="Confirmar contraseña", tamano=15, accion = self.cambio_contrasena)
        
        center_layout.addWidget(self.texto1)
        center_layout.addWidget(self.texto2)
        center_layout.addWidget(self.contraseña)
        center_layout.addWidget(self.repetir_contraseña)
        center_layout.addWidget(self.cambiar_contrasena)

        main_layout.addLayout(center_layout)

    def set_nombre_especialista(self, nombre: str):
        self.nombre_especialista = (nombre or "Especialista").strip() or "Especialista"
        self.texto1.setText(f"Hola {self.nombre_especialista}")

    def cambio_contrasena(self):
        self.router.show_specialist_login()
