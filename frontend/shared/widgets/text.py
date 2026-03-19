from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QLineEdit, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QFontMetrics, QIcon, QAction

PRIMARY = "#0E4C66"

class TextoInicio(QWidget):
    clicked = pyqtSignal()

    def __init__(self, label: str = "", tamano: int = 11, negrita: bool = False, error:bool = False, upper: bool = False, color: str = PRIMARY, accion=None, parent=None):
        super().__init__(parent)
        if error:
            color="#FF0000"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lbl = QLabel(label)
        if upper:
            self.lbl.setText(self.lbl.text().upper())
        font = QFont("Segoe UI", tamano)
        font.setBold(negrita)
        self.lbl.setFont(font)
        self.lbl.setStyleSheet(f"color: {color};")
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.lbl)

        if accion is not None:
            self.lbl.setStyleSheet(f"color: {color}; text-decoration: underline;")
            self.lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            self.clicked.connect(accion)
            self.lbl.mousePressEvent = self._on_label_clicked

    def _on_label_clicked(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def setText(self, texto: str):
        self.lbl.setText(texto)

    def text(self) -> str:
        return self.lbl.text()

class DatosPerfil(QWidget):
    def __init__(self, label: str, label2: str, tamano:int=15, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignRight)
        layout.setSpacing(50)
        
        lbl = TextoInicio(label, tamano=tamano)
        lbl.setMinimumWidth(200)
        lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        lbl.setStyleSheet(f"color: {PRIMARY};")
        #lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(lbl)

        self.dato = TextoInicio(label2, tamano=tamano)
    
        self.dato.setMinimumHeight(34)
        self.dato.setFixedWidth(250)
        self.dato.setFont(QFont("Segoe UI", tamano))        
        layout.addWidget(self.dato)
    

class FormField(QWidget):
    def __init__(self, label: str, placeholder: str = "", tamano:int=15, password: bool = False, negrita: bool = True, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignRight)
        layout.setSpacing(50)
        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", tamano))
        if negrita:
            lbl.setFont(QFont("Segoe UI", tamano, QFont.Weight.Bold))
        text_width = QFontMetrics(lbl.font()).horizontalAdvance(label)
        
        lbl.setMinimumWidth(200)
        lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        lbl.setStyleSheet(f"color: {PRIMARY};")
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft )
        layout.addWidget(lbl)

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.input.setMinimumHeight(34)
        self.input.setFixedWidth(250)
        self.input.setFont(QFont("Segoe UI", tamano))
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background: white;
                border: 1px solid {PRIMARY};
                border-radius: 4px;
                padding: 4px 10px;
                color: {PRIMARY};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {PRIMARY};
            }}
        """)
        if password:
            self.input.setEchoMode(QLineEdit.EchoMode.Password)

            self._icono_ojo_apagado = QIcon("assets/images/ojo_apagado.png")
            self._icono_ojo_encendido = QIcon("assets/images/ojo_encendido.png")
            self._icono_ojo = QAction(self._icono_ojo_apagado, "Mostrar/ocultar contrasena", self.input)
            self._icono_ojo.setCheckable(True)
            self._icono_ojo.triggered.connect(self._toggle_password)
            self.input.addAction(self._icono_ojo, QLineEdit.ActionPosition.TrailingPosition)
        layout.addWidget(self.input)
    
    def _toggle_password(self, checked: bool):
        if checked:
            self.input.setEchoMode(QLineEdit.EchoMode.Normal)
            self._icono_ojo.setIcon(self._icono_ojo_encendido)
        else:
            self.input.setEchoMode(QLineEdit.EchoMode.Password)
            self._icono_ojo.setIcon(self._icono_ojo_apagado)
    
    def text(self) -> str:
        return self.input.text()