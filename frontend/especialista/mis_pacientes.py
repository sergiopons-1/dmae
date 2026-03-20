from shared.widgets.especialista.sidebar import Sidebar
from shared.widgets.text import TextoInicio
from shared.widgets.buttons import PrimaryButton
from shared.widgets.tabla import TablaPacientes
from api_cliente import obtener_pacientes_clinica
from PyQt6.QtWidgets import (
    QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

PRIMARY    = "#0E4C66"
BG_COLOR   = "#FFF7E7"


class PacientesEspecialista(QWidget):
    def __init__(self, router, nombre="Carlos Mateo"):
        super().__init__()
        self.router = router
        self.nombre_especialista = nombre
        self._datos = []
        self._datos_filtrados = []
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────
        self.sidebar = Sidebar(nombre=nombre, parent=self)
        self.sidebar.go_logout.connect(self.router.show_inicio)
        self.sidebar.go_perfil.connect(self.router.show_perfil_especialista)
        main.addWidget(self.sidebar)

        # ── Contenido ────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet(f"background-color: {BG_COLOR};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 30, 40, 20)
        content_layout.setSpacing(20)

        # Título
        titulo = TextoInicio(label="PACIENTES", tamano=22, negrita=True)
        content_layout.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignHCenter)

        # ── Barra: búsqueda + botón ───────────────────────────
        bar_layout = QHBoxLayout()
        bar_layout.setSpacing(12)

        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar")
        self.buscador.setMinimumHeight(40)
        self.buscador.setFont(QFont("Segoe UI", 12))
        self.buscador.setStyleSheet(f"""
            QLineEdit {{
                background: white;
                border: 1.5px solid {PRIMARY};
                border-radius: 6px;
                padding: 4px 12px;
                color: {PRIMARY};
            }}
        """)
        self.buscador.textChanged.connect(self._on_buscar)
        bar_layout.addWidget(self.buscador, stretch=1)

        btn_alta = PrimaryButton(text="Dar de alta", tamano=13, accion=self._dar_de_alta)
        btn_alta.setFixedSize(180, 40)
        bar_layout.addWidget(btn_alta)

        content_layout.addLayout(bar_layout)

        # ── Tabla ────────────────────────────────────────────
        self.tabla = TablaPacientes()
        self.tabla.fila_clickada.connect(self._ir_a_progreso_paciente)
        content_layout.addWidget(self.tabla)

        # content_layout.addLayout(pag_layout)
        main.addWidget(content, stretch=1)
        main.setStretch(0, 3)
        main.setStretch(1, 7)

        self._actualizar_tabla()

    def set_nombre_especialista(self, nombre: str):
        self.nombre_especialista = (nombre or "Especialista").strip() or "Especialista"
        self.sidebar.set_nombre(self.nombre_especialista)

    # ── Datos ─────────────────────────────────────────────────
    def recargar_pacientes(self):
        clinic_id = getattr(self.router, "clinic_id", None)
        token = getattr(self.router, "auth_token", None)

        if not clinic_id:
            self._datos = []
            self._datos_filtrados = []
            self._actualizar_tabla()
            return

        status_code, data = obtener_pacientes_clinica(clinic_id, token)
        if status_code == 200 and isinstance(data, list):
            self._datos = data
        else:
            self._datos = []

        self._datos_filtrados = self._datos.copy()
        self._actualizar_tabla()

    def cargar_datos(self, datos: list):
        """
        Método público para cargar datos desde la API.
        datos: lista de dicts con claves: nombre, apellidos, rehabilitaciones, especialista
        """
        self._datos = datos
        self._datos_filtrados = datos.copy()
        self._actualizar_tabla()

    # ── Tabla ─────────────────────────────────────────────────
    def _actualizar_tabla(self):
        self.tabla.set_datos(self._datos_filtrados)

    # ── Búsqueda ──────────────────────────────────────────────
    def _on_buscar(self, texto: str):
        texto = texto.lower().strip()
        if texto:
            self._datos_filtrados = [
                p for p in self._datos
                if texto in p["nombre"].lower()
                or texto in p["apellidos"].lower()
            ]
        else:
            self._datos_filtrados = self._datos.copy()
        self._actualizar_tabla()

    # ── Acción botón ──────────────────────────────────────────
    def _dar_de_alta(self):
        self.router.show_registrar_paciente()

    def _ir_a_progreso_paciente(self, paciente: dict):
        self.router.show_progreso_individual(paciente)

