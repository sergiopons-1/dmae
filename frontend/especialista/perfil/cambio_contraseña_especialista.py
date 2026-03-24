from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt
from shared.widgets.buttons import PrimaryButton, BackButton
from shared.widgets.fondo import BeigeBg
from shared.widgets.text import FormField, TextoInicio
from shared.widgets.imagenes import Imagenes
from shared.widgets.layout import MainLayout, CenterLayout
from api_cliente import cambiar_contrasena_especialista


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
        self.contraseña = FormField(label="Nueva Contraseña", tamano=14, password=True)
        self.repetir_contraseña = FormField(label="Repetir contraseña", tamano=14, password=True)
        self.label_error = TextoInicio(label="", tamano=12, error=True)
        self.label_error.setVisible(False)
        self.cambiar_contrasena = PrimaryButton(text="Confirmar contraseña", tamano=15, accion = self.cambio_contrasena)
        self.back_button = BackButton(accion=self.volver)
        
        center_layout.addWidget(self.texto1)
        center_layout.addWidget(self.texto2)
        center_layout.addWidget(self.contraseña)
        center_layout.addWidget(self.repetir_contraseña)
        center_layout.addWidget(self.label_error)
        center_layout.addWidget(self.cambiar_contrasena)
        center_layout.addWidget(self.back_button)

        main_layout.addLayout(center_layout)

    def set_nombre_especialista(self, nombre: str):
        self.nombre_especialista = (nombre or "Especialista").strip() or "Especialista"
        self.texto1.setText(f"Hola {self.nombre_especialista}")
    
    def volver(self):
        self.router.show_perfil_especialista()

    def cambio_contrasena(self):
        nueva = self.contraseña.text().strip()
        repetida = self.repetir_contraseña.text().strip()

        self.label_error.setVisible(False)

        if not nueva or not repetida:
            self.label_error.setText("Debes completar ambos campos")
            self.label_error.setVisible(True)
            return

        if nueva != repetida:
            self.label_error.setText("Las contraseñas no coinciden")
            self.label_error.setVisible(True)
            return

        token = getattr(self.router, "auth_token", None)
        if not token:
            self.label_error.setText("Tu sesión no es valida. Inicia sesión de nuevo")
            self.label_error.setVisible(True)
            return

        status_code, data = cambiar_contrasena_especialista(password=nueva, token=token)

        if status_code == 200:
            self.contraseña.input.clear()
            self.repetir_contraseña.input.clear()
            self.router.show_specialist_login()
            if hasattr(self.router.iniciar_sesion, "mostrar_banner_exito"):
                self.router.iniciar_sesion.mostrar_banner_exito("contraseña cambiada correctamente", duracion_ms=3000)
            return

        if status_code in (400, 401, 403):
            self.label_error.setText(data.get("error", "No se pudo cambiar la contraseña"))
            self.label_error.setVisible(True)
            return

        if status_code is None:
            self.label_error.setText(data.get("error", "No se pudo conectar al servidor"))
            self.label_error.setVisible(True)
            return

        self.label_error.setText("Error inesperado, intenta de nuevo")
        self.label_error.setVisible(True)
