from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QDialog, QVBoxLayout, QTextEdit, QMessageBox, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from shared.widgets.buttons import PrimaryButton
from shared.widgets.layout import CenterLayout
from shared.widgets.especialista.sidebar import Sidebar
from shared.widgets.text import TextoInicio, FormField
from api_cliente import crear_nota

PRIMARY = "#0E4C66"
BG_COLOR = "#FFF7E7"

class PublicarNota(QDialog):
    def __init__(self, router, nombre="Carlos Mateo"):
        super().__init__()
        self.router = router
        self.nombre_especialista = nombre
        self._paciente_id = None
        self._nombre_paciente = nombre

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        self.sidebar = Sidebar(nombre=nombre, parent=self)
        self.sidebar.go_logout.connect(self.router.show_inicio)
        main.addWidget(self.sidebar)

        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        center_layout.setSpacing(25)
        center_layout.setContentsMargins(40, 30, 40, 20)

        # Título principal
        self.label = TextoInicio(label="Añadir nota", tamano=22, upper= True, negrita=True)
        
        # Subtítulo con nombre del paciente
        self.titulo_nota = TextoInicio(label=f"Nueva nota para {nombre}", tamano=13)
    
        # Línea separadora
        separador = QWidget()
        separador.setFixedHeight(2)
        separador.setStyleSheet(f"background-color: {PRIMARY};")
        
        # Campo de texto para la nota
        self.campo_nota = QTextEdit()
        self.campo_nota.setPlaceholderText("Escriba aquí la nota sobre el paciente...")
        self.campo_nota.setMinimumHeight(250)
        self.campo_nota.setStyleSheet(f"""
            QTextEdit {{
                background-color: {BG_COLOR};
                border: 2px solid {PRIMARY};
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                font-family: Segoe UI;
                color: {PRIMARY};
            }}
        """)
        
        self.boton_publicar = PrimaryButton(text="PUBLICAR NOTA", tamano=16, accion=self.publicar_nota)

        center_layout.addWidget(self.label)
        center_layout.addWidget(self.titulo_nota)
        center_layout.addWidget(separador, alignment=Qt.AlignmentFlag.AlignHCenter)
        center_layout.addSpacing(10)
        center_layout.addWidget(self.campo_nota, alignment=Qt.AlignmentFlag.AlignHCenter)
        center_layout.addSpacing(15)
        center_layout.addWidget(self.boton_publicar, alignment=Qt.AlignmentFlag.AlignHCenter)
        center_layout.addStretch()

        center_widget = QWidget()
        center_widget.setStyleSheet(f"background-color: {BG_COLOR};")
        center_widget.setLayout(center_layout)
        main.addWidget(center_widget, stretch=1)

    def set_nombre_especialista(self, nombre: str):
        self.nombre_especialista = (nombre or "Especialista").strip() or "Especialista"
        self.sidebar.set_nombre(self.nombre_especialista)
        self.titulo_nota.setText(f"Nueva nota para {self._nombre_paciente}")

    def set_paciente_id(self, paciente_id: int, nombre_paciente: str = ""):
        self._paciente_id = paciente_id
        self._nombre_paciente = nombre_paciente or self.nombre_especialista
        self.titulo_nota.setText(f"Nueva nota para {self._nombre_paciente}")
        self.campo_nota.clear()

    def publicar_nota(self):
        contenido = self.campo_nota.toPlainText().strip()
        
        if not contenido:
            QMessageBox.warning(self, "Advertencia", "Por favor, escriba una nota antes de publicar.")
            return
        
        if not self._paciente_id:
            QMessageBox.critical(self, "Error", "No se ha seleccionado un paciente.")
            return
        
        token = getattr(self.router, "auth_token", None)
        status_code, response = crear_nota(self._paciente_id, contenido, token)
        
        if status_code == 201:
            QMessageBox.information(self, "Éxito", "Nota publicada correctamente.")
            if hasattr(self.router.progreso_individual, "agregar_nota_local"):
                self.router.progreso_individual.agregar_nota_local(
                    contenido=contenido,
                    fecha_iso=response.get("fecha") if isinstance(response, dict) else None,
                )
            self.router.show_progreso_individual()
        else:
            error_msg = response.get("error", "Error al publicar la nota")
            QMessageBox.critical(self, "Error", error_msg)