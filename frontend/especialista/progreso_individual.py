from shared.widgets.especialista.sidebar import Sidebar
from shared.widgets.text import TextoInicio
from shared.widgets.buttons import PrimaryButton
from shared.widgets.tabla import TablaPacientes
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QWidget, QStackedWidget, QPushButton, QButtonGroup
)
from PyQt6.QtCore import Qt

PRIMARY    = "#0E4C66"
BG_COLOR   = "#FFF7E7"

class ProgresoIndividual(QWidget):
    def __init__(self, router, nombre="Carlos Mateo"):
        super().__init__()
        self.router = router
        self._nombre_paciente = nombre
        self._datos_progreso = []
        self._notas_por_paciente = {
            "ANTONIO RODRIGUEZ DOMINGUEZ": [
                {"Numero de nota": "7", "Descripcion": "Mejora en seguimiento visual horizontal.", "Fecha de emision": "2026-03-05"},
                {"Numero de nota": "6", "Descripcion": "Reduce tiempo de reaccion en tareas de fijacion.", "Fecha de emision": "2026-02-26"},
                {"Numero de nota": "5", "Descripcion": "Mantener ejercicios de precision 3 veces por semana.", "Fecha de emision": "2026-02-14"},
                {"Numero de nota": "4", "Descripcion": "Sin molestias reportadas tras la sesion.", "Fecha de emision": "2026-02-02"},
            ],
            "MARTA LOPEZ GARCIA": [
                {"Numero de nota": "4", "Descripcion": "Buena adherencia al plan semanal.", "Fecha de emision": "2026-03-04"},
                {"Numero de nota": "3", "Descripcion": "Aumento progresivo en puntuacion general.", "Fecha de emision": "2026-02-20"},
                {"Numero de nota": "2", "Descripcion": "Revisar fatiga ocular en sesiones largas.", "Fecha de emision": "2026-02-09"},
            ],
            "LUCIA FERNANDEZ MORA": [
                {"Numero de nota": "9", "Descripcion": "Presenta estabilidad en movimientos sacadicos.", "Fecha de emision": "2026-03-06"},
                {"Numero de nota": "8", "Descripcion": "Completa ejercicios sin incidencias.", "Fecha de emision": "2026-02-27"},
                {"Numero de nota": "7", "Descripcion": "Proponer incremento de dificultad en siguiente ciclo.", "Fecha de emision": "2026-02-16"},
            ],
        }

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

        # Titulo
        self.titulo_progreso = TextoInicio(label="Progreso de " + nombre, tamano=22, negrita=True, upper=True)
        content_layout.addWidget(self.titulo_progreso, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Switch segmentado: progreso <-> notas
        toggle_layout = QHBoxLayout()
        toggle_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        toggle_layout.setSpacing(0)

        self.switch_container = QWidget()
        self.switch_container.setStyleSheet(
            f"""
            QWidget {{
                border: 1px solid {PRIMARY};
                border-radius: 16px;
                background-color: #E7EFF2;
            }}
            QPushButton {{
                border: none;
                background-color: transparent;
                color: {PRIMARY};
                font-size: 12px;
                font-weight: bold;
                padding: 8px 16px;
                min-width: 120px;
            }}
            QPushButton:checked {{
                background-color: {PRIMARY};
                color: white;
            }}
            """
        )
        switch_layout = QHBoxLayout(self.switch_container)
        switch_layout.setContentsMargins(0, 0, 0, 0)
        switch_layout.setSpacing(0)

        self.btn_switch_progreso = QPushButton("PROGRESO")
        self.btn_switch_progreso.setCheckable(True)
        self.btn_switch_notas = QPushButton("NOTAS")
        self.btn_switch_notas.setCheckable(True)

        self.switch_group = QButtonGroup(self)
        self.switch_group.setExclusive(True)
        self.switch_group.addButton(self.btn_switch_progreso)
        self.switch_group.addButton(self.btn_switch_notas)

        switch_layout.addWidget(self.btn_switch_progreso)
        switch_layout.addWidget(self.btn_switch_notas)
        toggle_layout.addWidget(self.switch_container)
        content_layout.addLayout(toggle_layout)

        self.btn_switch_progreso.clicked.connect(lambda: self._cambiar_vista("progreso"))
        self.btn_switch_notas.clicked.connect(lambda: self._cambiar_vista("notas"))

        # Vista progreso
        self.vista_progreso = QWidget()
        vista_progreso_layout = QVBoxLayout(self.vista_progreso)
        vista_progreso_layout.setContentsMargins(0, 0, 0, 0)
        self.tabla_progreso = TablaPacientes(columnas=5, headers=["Número", "Fecha inicio", "Fecha fin", "Estado", "Puntuación"])
        vista_progreso_layout.addWidget(self.tabla_progreso)

        # Vista notas
        self.vista_notas = QWidget()
        vista_notas_layout = QVBoxLayout(self.vista_notas)
        vista_notas_layout.setContentsMargins(0, 0, 0, 18)
        vista_notas_layout.setSpacing(16)

        self.boton = PrimaryButton(text="Añadir nota", tamano=20, accion=self.anadir_nota)
        vista_notas_layout.addWidget(self.boton, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.tabla_notas = TablaPacientes(columnas=3, headers=["Número de nota", "Descripción", "Fecha de emisión"])
        vista_notas_layout.addWidget(self.tabla_notas)
        vista_notas_layout.addSpacing(10)

        self.panel_vistas = QStackedWidget()
        self.panel_vistas.addWidget(self.vista_progreso)
        self.panel_vistas.addWidget(self.vista_notas)
        self.panel_vistas.setCurrentWidget(self.vista_progreso)
        content_layout.addWidget(self.panel_vistas)

        self.btn_switch_progreso.setChecked(True)
        self._cambiar_vista("progreso")

        main.addWidget(content, stretch=1)

        # Cargar datos de ejemplo
        self._cargar_datos_ejemplo()
        self._actualizar_notas_tabla()

    # ── Datos ─────────────────────────────────────────────────
    def _cargar_datos_ejemplo(self):
        """Sustituye este método por la llamada real a la API Django."""
        self._datos_progreso = [
            {"Número": "1", "Fecha inicio": "2024-01-01", "Fecha fin": "2023-01-31", "Estado": "Completado", "Puntuación": 8.5},
            {"Número": "2", "Fecha inicio": "2025-02-01", "Fecha fin": "2023-02-28", "Estado": "En curso", "Puntuación": 7.0},
            {"Número": "3", "Fecha inicio": "2020-03-01", "Fecha fin": "2023-03-31", "Estado": "Pendiente", "Puntuación": 6.5},
            {"Número": "4", "Fecha inicio": "2021-04-01", "Fecha fin": "2023-04-30", "Estado": "Completado", "Puntuación": 8.1},
            {"Número": "5", "Fecha inicio": "2026-01-01", "Fecha fin": "2023-05-31", "Estado": "Completado", "Puntuación": 8.7},
            {"Número": "6", "Fecha inicio": "2019-06-01", "Fecha fin": "2023-06-30", "Estado": "En curso", "Puntuación": 7.8},
        ]
        self._actualizar_tabla()

    def cargar_datos(self, datos: list):
        """
        Método público para cargar datos desde la API.
        datos: lista de dicts con claves: nombre, apellidos, rehabilitaciones, especialista
        """
        self._datos_progreso = datos
        self._actualizar_tabla()

    # ── Tabla ─────────────────────────────────────────────────
    def _actualizar_tabla(self):
        datos_ordenados = sorted(
            self._datos_progreso,
            key=lambda item: item.get("Fecha inicio", ""),
        )
        self.tabla_progreso.set_datos(datos_ordenados)

    # ── Acción botón ──────────────────────────────────────────
    def anadir_nota(self):
        self.router.show_publicar_nota_paciente()

    def set_paciente(self, paciente: dict):
        nombre = paciente.get("nombre", "")
        apellidos = paciente.get("apellidos", "")
        nombre_completo = f"{nombre} {apellidos}".upper().strip()
        self._nombre_paciente = nombre_completo or "PACIENTE"
        self._actualizar_titulo_segun_vista()
        self._actualizar_notas_tabla()

    def _actualizar_notas_tabla(self):
        notas = self._notas_por_paciente.get(self._nombre_paciente, [])

        if notas:
            ultimas_tres = sorted(
                notas,
                key=lambda n: n.get("Fecha de emisión", ""),
                reverse=True,
            )[:3]
        else:
            ultimas_tres = [
                {
                    "Número de nota": "-",
                    "Descripción": "Sin notas registradas aun.",
                    "Fecha de emisión": "-",
                },
                {
                    "Número de nota": "-",
                    "Descripción": "Sin notas registradas aun.",
                    "Fecha de emisión": "-",
                },
                {
                    "Número de nota": "-",
                    "Descripción": "Sin notas registradas aun.",
                    "Fecha de emisión": "-",
                },
            ]

        self.tabla_notas.set_datos(ultimas_tres)

    def _cambiar_vista(self, modo: str):
        if modo == "notas":
            self.panel_vistas.setCurrentWidget(self.vista_notas)
            self.btn_switch_notas.setChecked(True)
        else:
            self.panel_vistas.setCurrentWidget(self.vista_progreso)
            self.btn_switch_progreso.setChecked(True)

        self._actualizar_titulo_segun_vista()

    def _actualizar_titulo_segun_vista(self):
        if self.panel_vistas.currentWidget() == self.vista_notas:
            self.titulo_progreso.setText(f"NOTAS DE {self._nombre_paciente}")
        else:
            self.titulo_progreso.setText(f"PROGRESO DE {self._nombre_paciente}")

    

