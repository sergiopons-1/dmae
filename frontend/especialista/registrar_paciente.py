from datetime import datetime

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QDialog)
from PyQt6.QtCore import Qt
from api_cliente import singin_paciente
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
        self.DNI = FormField(label="DNI:", placeholder="12345678", tamano=15)
        self.nombre = FormField(label="Nombre:", placeholder="Nombre", tamano=15)
        self.apellidos = FormField(label="Apellidos:", placeholder="Apellidos", tamano=15)
        self.fechaNacimiento = FormField(label="Fecha de nacimiento:", placeholder="DD/MM/AAAA", tamano=15)
        self.correo = FormField(label="Correo electrónico:", placeholder="example@example.com", tamano=15)
        self.label_error = TextoInicio(label="", tamano=12, error=True)
        self.label_error.setVisible(False)
        self.cambiar_contrasena = PrimaryButton(text="GENERAR CÓDIGO", tamano=15, accion=self.generar_codigo)
        

        center_layout.addWidget(self.label)
        center_layout.addWidget(self.DNI)
        center_layout.addWidget(self.nombre)
        center_layout.addWidget(self.apellidos)
        center_layout.addWidget(self.fechaNacimiento)
        center_layout.addWidget(self.correo)
        center_layout.addWidget(self.label_error)
        center_layout.addWidget(self.cambiar_contrasena)

        center_widget = QWidget()
        center_widget.setStyleSheet("background-color: #FFF7E7;")
        center_widget.setLayout(center_layout)
        main.addWidget(center_widget)

    def set_nombre_especialista(self, nombre: str):
        self.nombre_especialista = (nombre or "Especialista").strip() or "Especialista"
        self.sidebar.set_nombre(self.nombre_especialista)

    def generar_codigo(self):
        dni = self.DNI.text().strip()
        first_name = self.nombre.text().strip()
        last_name = self.apellidos.text().strip()
        birth_date = self.fechaNacimiento.text().strip()
        email = self.correo.text().strip()

        self.label_error.setVisible(False)

        if not all([dni, first_name, last_name, birth_date, email]):
            self.label_error.setText("Todos los campos son obligatorios")
            self.label_error.setVisible(True)
            return

        if not dni.isdigit() or len(dni) != 8:
            self.label_error.setText("El DNI debe contener exactamente 8 dígitos")
            self.label_error.setVisible(True)
            return

        try:
            fecha = datetime.strptime(birth_date, "%d/%m/%Y").date()
        except ValueError:
            self.label_error.setText("La fecha debe tener formato DD/MM/AAAA")
            self.label_error.setVisible(True)
            return

        token = getattr(self.router, "auth_token", None)
        status_code, data = singin_paciente(
            dni=dni,
            email=email,
            first_name=first_name,
            last_name=last_name,
            birth_date=fecha.isoformat(),
            token=token,
        )

        if status_code == 201:
            codigo = data.get("codigo", "")
            self.router.show_generar_codigo(codigo)
            self.DNI.input.clear()
            self.nombre.input.clear()
            self.apellidos.input.clear()
            self.fechaNacimiento.input.clear()
            self.correo.input.clear()
            return

        if status_code in (400, 401, 403):
            self.label_error.setText(data.get("error", "No se pudo registrar al paciente"))
            self.label_error.setVisible(True)
            return

        if status_code is None:
            self.label_error.setText(data.get("error", "No se pudo conectar al servidor"))
            self.label_error.setVisible(True)
            return

        self.label_error.setText("Error inesperado, intenta de nuevo")
        self.label_error.setVisible(True)