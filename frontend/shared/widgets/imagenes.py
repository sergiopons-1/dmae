from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class Imagenes(QLabel):
    def __init__(self, enlace: str, ancho: int = 120, alto: int = 120, parent=None):
        super().__init__(parent)

        pixmap = QPixmap(enlace)

        if pixmap.isNull():
            self.setText(f"[imagen no encontrada]")
            self.setStyleSheet("color: red; font-size: 10px;")
        else:
            pixmap = pixmap.scaled(
                ancho, alto,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(pixmap)

        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setFixedSize(ancho, alto)
