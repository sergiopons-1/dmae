from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QTimer
from PyQt6.QtGui import QFont, QColor
from shared.widgets.buttons import PaginationButton
from shared.widgets.text import TextoInicio


PRIMARY = "#0E4C66"
SECONDARY = "#FFF0D2"
SECONDARY_HOVER = "#FEE5B4"
SECONDARY_SELECTED = "#FCF6EB"
BORDER = "#0E4C66"

class TablaPacientes(QWidget):
    fila_clickada = pyqtSignal(dict)

    def __init__(self, columnas: int=4, min_height: int=400, headers: list=["Nombre", "Apellidos", "Rehabilitaciones", "Especialista"]):
        super().__init__()

        self._headers = headers[:columnas]

        self._datos = []
        self._datos_filtrados = []
        self._pagina_actual = 0
        self._alto_fila = 46
        self._filas_por_pagina = 1
        self._pagina_actual_datos = []
        self._fila_hover = -1

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(columnas)
        self.tabla.setHorizontalHeaderLabels(self._headers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.setShowGrid(False)
        self.tabla.setAlternatingRowColors(False)
        self.tabla.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tabla.setMouseTracking(True)
        self.tabla.setWordWrap(True)
        self.tabla.setMinimumHeight(min_height)
        self.tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabla.cellClicked.connect(self._on_fila_click)
        self.tabla.cellEntered.connect(self._on_fila_hover)
        self.tabla.itemSelectionChanged.connect(self._repintar_filas)
        self.tabla.viewport().installEventFilter(self)
        self.tabla.setStyleSheet(f"""
            QTableWidget {{
                background-color: {SECONDARY};
                border: 1.5px solid {BORDER};
                border-radius: 5px;
                color: {PRIMARY};
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 10px 8px;
                border-bottom: 1px solid #D0E0E0;
                color: {PRIMARY};
            }}
            
            QHeaderView::section {{
                background-color: {SECONDARY};
                color: {PRIMARY};
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-bottom: 1.5px solid {BORDER};
                padding: 10px 8px;
            }}
            
        """)
        # ── Paginación ───────────────────────────────────────
        pag_layout = QHBoxLayout()
        pag_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pag_layout.setSpacing(20)

        self.btn_anterior = PaginationButton("<", self._pagina_anterior)

        self.lbl_pagina = TextoInicio(label="1 de 1", tamano=12, color=PRIMARY)
        
        self.btn_siguiente = PaginationButton(">", self._pagina_siguiente)
        
        pag_layout.addWidget(self.btn_anterior)
        pag_layout.addWidget(self.lbl_pagina)
        pag_layout.addWidget(self.btn_siguiente)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(14)
        layout_principal.addWidget(self.tabla)
        layout_principal.addLayout(pag_layout)

        self._recalcular_filas_por_pagina()
        self._actualizar_tabla()


        # ── Tabla ─────────────────────────────────────────────────
    def set_datos(self, datos):
        self._datos = datos or []
        self._datos_filtrados = list(self._datos)
        self._pagina_actual = 0
        self._recalcular_filas_por_pagina()
        self._actualizar_tabla()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._recalcular_filas_por_pagina()

    def showEvent(self, event):
        super().showEvent(event)
        # Espera al siguiente ciclo para que el layout termine y el viewport tenga alto real.
        QTimer.singleShot(0, self._recalcular_filas_por_pagina)

    def _recalcular_filas_por_pagina(self):
        disponibles = self.tabla.viewport().height()
        nuevas_filas = max(1, disponibles // self._alto_fila)

        if nuevas_filas != self._filas_por_pagina:
            primer_indice = self._pagina_actual * self._filas_por_pagina
            self._filas_por_pagina = nuevas_filas
            self._pagina_actual = primer_indice // self._filas_por_pagina
            self._actualizar_tabla()

    def _actualizar_tabla(self):
        inicio = self._pagina_actual * self._filas_por_pagina
        fin = inicio + self._filas_por_pagina
        pagina = self._datos_filtrados[inicio:fin]
        self._pagina_actual_datos = pagina

        self.tabla.setRowCount(len(pagina))

        for fila, paciente in enumerate(pagina):
            valores = [self._valor_columna(paciente, header) for header in self._headers]
            for col, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(QFont("Segoe UI", 12))
                item.setForeground(QColor(PRIMARY))
                self.tabla.setItem(fila, col, item)

            self.tabla.setRowHeight(fila, self._alto_fila)

        # Si existe columna de descripcion, ajusta filas al contenido para soportar multilinea
        # tras redimensionar la ventana o la tabla.
        if any(str(h).strip().lower() == "descripción" for h in self._headers):
            self.tabla.resizeRowsToContents()
            for fila in range(self.tabla.rowCount()):
                if self.tabla.rowHeight(fila) < self._alto_fila:
                    self.tabla.setRowHeight(fila, self._alto_fila)

        self._repintar_filas()
        self._actualizar_paginacion()

    def _actualizar_paginacion(self):
        total = len(self._datos_filtrados)
        total_paginas = max(1, -(-total // self._filas_por_pagina))
        pagina_mostrar = self._pagina_actual + 1

        self.lbl_pagina.setText(f"{pagina_mostrar} de {total_paginas}")
        self.btn_anterior.setEnabled(self._pagina_actual > 0)
        self.btn_siguiente.setEnabled(self._pagina_actual < total_paginas - 1)

    # ── Paginación ────────────────────────────────────────────
    def _pagina_anterior(self):
        if self._pagina_actual > 0:
            self._pagina_actual -= 1
            self._actualizar_tabla()

    def _pagina_siguiente(self):
        total_paginas = max(1, -(-len(self._datos_filtrados) // self._filas_por_pagina))
        if self._pagina_actual < total_paginas - 1:
            self._pagina_actual += 1
            self._actualizar_tabla()

    def _on_fila_click(self, fila, _columna):
        if 0 <= fila < len(self._pagina_actual_datos):
            self.fila_clickada.emit(self._pagina_actual_datos[fila])

    def _on_fila_hover(self, fila, _columna):
        if fila != self._fila_hover:
            self._fila_hover = fila
            self._repintar_filas()

    def eventFilter(self, source, event):
        if source is self.tabla.viewport() and event.type() == QEvent.Type.Leave:
            if self._fila_hover != -1:
                self._fila_hover = -1
                self._repintar_filas()
        return super().eventFilter(source, event)

    def _repintar_filas(self):
        seleccion_model = self.tabla.selectionModel()
        filas_seleccionadas = set()
        if seleccion_model is not None:
            filas_seleccionadas = {index.row() for index in seleccion_model.selectedRows()}

        for fila in range(self.tabla.rowCount()):
            if fila in filas_seleccionadas:
                color_fondo = QColor(SECONDARY_SELECTED)
            elif fila == self._fila_hover:
                color_fondo = QColor(SECONDARY_HOVER)
            else:
                color_fondo = QColor(SECONDARY)

            for col in range(self.tabla.columnCount()):
                item = self.tabla.item(fila, col)
                if item is not None:
                    item.setBackground(color_fondo)
                    item.setForeground(QColor(PRIMARY))

    def _valor_columna(self, fila_datos: dict, header: str):
        if not isinstance(fila_datos, dict):
            return ""

        if header in fila_datos:
            return fila_datos[header]

        header_minuscula = header.lower()
        if header_minuscula in fila_datos:
            return fila_datos[header_minuscula]

        return ""
