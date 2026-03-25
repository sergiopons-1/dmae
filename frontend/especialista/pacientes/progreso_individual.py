from shared.widgets.sidebar import SidebarEspecialista
from shared.widgets.text import TextoInicio
from shared.widgets.buttons import PrimaryButton, BackButton
from shared.widgets.tabla import TablaPacientes
from shared.widgets.banner import Banner
from api_cliente import obtener_progreso_individual
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QWidget, QStackedWidget, QPushButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from datetime import datetime

PRIMARY    = "#0E4C66"
BG_COLOR   = "#FFF7E7"
MAX_DESC_NOTA = 250
MAX_TITULO_PACIENTE = 30

class ProgresoIndividual(QWidget):
    def __init__(self, router, nombre=""):
        super().__init__()
        self.router = router
        self.nombre_especialista = nombre
        self._nombre_paciente = nombre
        self._paciente_id = None
        self._datos_progreso = []
        self._notas = []

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────
        self.sidebar = SidebarEspecialista(nombre=nombre, parent=self)
        self.sidebar.go_logout.connect(self.router.show_inicio)
        self.sidebar.go_perfil.connect(self.router.show_perfil_especialista)
        main.addWidget(self.sidebar)

        # ── Contenido ────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet(f"background-color: {BG_COLOR};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 30, 40, 20)
        content_layout.setSpacing(20)

        self.banner_exito = Banner(self)
        content_layout.addWidget(self.banner_exito)

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
        self.back_button = BackButton(accion=self.volver)
        vista_progreso_layout.addWidget(self.tabla_progreso)
        vista_progreso_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Vista notas
        self.vista_notas = QWidget()
        vista_notas_layout = QVBoxLayout(self.vista_notas)
        vista_notas_layout.setContentsMargins(0, 0, 0, 18)
        vista_notas_layout.setSpacing(16)

        self.boton = PrimaryButton(text="Añadir nota", tamano=16, accion=self.anadir_nota)
        vista_notas_layout.addWidget(self.boton, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.tabla_notas = TablaPacientes(columnas=3, min_height=200, headers=["Número de nota", "Descripción", "Fecha de emisión"])
        self.back_button = BackButton(accion=self.volver)
        vista_notas_layout.addWidget(self.tabla_notas)
        vista_notas_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        

        self.panel_vistas = QStackedWidget()
        self.panel_vistas.addWidget(self.vista_progreso)
        self.panel_vistas.addWidget(self.vista_notas)
        self.panel_vistas.setCurrentWidget(self.vista_progreso)
        content_layout.addWidget(self.panel_vistas)

        self.btn_switch_progreso.setChecked(True)
        self._cambiar_vista("progreso")

        main.addWidget(content, stretch=1)

        self._actualizar_tabla()
        self._actualizar_notas_tabla()

    def volver(self):
        self.router.show_pacientes_especialista()

    def set_nombre_especialista(self, nombre: str):
        self.nombre_especialista = (nombre or "Especialista").strip() or "Especialista"
        self.sidebar.set_nombre(self.nombre_especialista)

    # ── Datos ─────────────────────────────────────────────────
    def cargar_datos(self, datos: list):
        """
        Método público para cargar datos desde la API.
        datos: lista de dicts con claves: nombre, apellidos, rehabilitaciones, especialista
        """
        self._datos_progreso = datos
        self._actualizar_tabla()

    # ── Tabla ─────────────────────────────────────────────────
    def _actualizar_tabla(self):
        if self._datos_progreso:
            datos_ordenados = sorted(
                self._datos_progreso,
                key=lambda item: item.get("Fecha inicio", ""),
            )
            self.tabla_progreso.set_datos(datos_ordenados)
            return

        self.tabla_progreso.set_datos([
            {
                "Número": "-",
                "Fecha inicio": "-",
                "Fecha fin": "-",
                "Estado": "Sin rehabilitaciones registradas",
                "Puntuación": "-",
            }
        ])

    
    def anadir_nota(self):
        self.router.show_publicar_nota_paciente()

    def set_paciente(self, paciente: dict):
        self._paciente_id = paciente.get("id")
        nombre = paciente.get("nombre", "")
        apellidos = paciente.get("apellidos", "")
        nombre_completo = f"{nombre} {apellidos}".upper().strip()
        self._nombre_paciente = nombre_completo or "PACIENTE"
        self._cambiar_vista("progreso")
        self._cargar_datos_reales()
        self._actualizar_notas_tabla()

    def _actualizar_notas_tabla(self):
        if self._notas:
            notas_mostradas = []
            for nota in self._notas:
                nota_formateada = dict(nota)
                descripcion = str(nota_formateada.get("Descripción", ""))
                if len(descripcion) > MAX_DESC_NOTA:
                    descripcion = descripcion[:MAX_DESC_NOTA]
                nota_formateada["Descripción"] = descripcion
                notas_mostradas.append(nota_formateada)

            self.tabla_notas.set_datos(notas_mostradas)
            return

        self.tabla_notas.set_datos([
            {
                "Número de nota": "-",
                "Descripción": "Sin notas registradas aún.",
                "Fecha de emisión": "-",
            }
        ])

    def agregar_nota_local(self, contenido: str, fecha_iso: str | None = None):
        fecha = "-"
        if fecha_iso:
            try:
                fecha = datetime.fromisoformat(fecha_iso.replace("Z", "+00:00")).date().isoformat()
            except ValueError:
                fecha = datetime.now().date().isoformat()
        else:
            fecha = datetime.now().date().isoformat()

        nueva_nota = {
            "Número de nota": "1",
            "Descripción": contenido,
            "Fecha de emisión": fecha,
        }

        self._notas.insert(0, nueva_nota)

        for indice, item in enumerate(self._notas, start=1):
            item["Número de nota"] = str(indice)

        self._actualizar_notas_tabla()

    def mostrar_banner_exito(self, mensaje: str, duracion_ms: int = 3000):
        self.banner_exito.mostrar(mensaje, tipo="success", duracion_ms=duracion_ms)

    def _ocultar_banner_exito(self):
        self.banner_exito.ocultar()

    def _cargar_datos_reales(self):
        token = getattr(self.router, "auth_token", None)
        if not self._paciente_id or not token:
            self._datos_progreso = []
            self._notas = []
            self._actualizar_tabla()
            return

        status_code, data = obtener_progreso_individual(self._paciente_id, token)
        if status_code == 200 and isinstance(data, dict):
            rehabilitaciones = data.get("rehabilitaciones", [])
            notas = data.get("notas", [])
            self._datos_progreso = rehabilitaciones if isinstance(rehabilitaciones, list) else []
            self._notas = notas if isinstance(notas, list) else []
        else:
            self._datos_progreso = []
            self._notas = []

        self._actualizar_tabla()

    def _cambiar_vista(self, modo: str):
        if modo == "notas":
            self.panel_vistas.setCurrentWidget(self.vista_notas)
            self.btn_switch_notas.setChecked(True)
        else:
            self.panel_vistas.setCurrentWidget(self.vista_progreso)
            self.btn_switch_progreso.setChecked(True)

        self._actualizar_titulo_segun_vista()

    def _texto_truncado(self, texto: str, max_chars: int) -> str:
        valor = (texto or "").strip()
        if len(valor) <= max_chars:
            return valor
        return f"{valor[:max_chars - 1]}…"

    def _actualizar_titulo_segun_vista(self):
        nombre_mostrado = self._texto_truncado(self._nombre_paciente, MAX_TITULO_PACIENTE)
        if self.panel_vistas.currentWidget() == self.vista_notas:
            self.titulo_progreso.setText(f"NOTAS DE {nombre_mostrado}")
        else:
            self.titulo_progreso.setText(f"PROGRESO DE {nombre_mostrado}")

        self.titulo_progreso.lbl.setToolTip(self._nombre_paciente)

    

