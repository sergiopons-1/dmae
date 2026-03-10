from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import Qt


class MainLayout(QVBoxLayout):
    def __init__(self, espacio: int=50):
        super().__init__() 
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(espacio)

class CenterLayout(QVBoxLayout):
    def __init__(self, espacio: int=50):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSpacing(espacio)

    def addWidget(self, widget, stretch=0, alignment=Qt.AlignmentFlag.AlignHCenter):
        super().addWidget(widget, stretch, alignment)

    def apply_responsive(self, width: int):
        if width < 900:
            self.setSpacing(16)
            self.setContentsMargins(12, 12, 12, 12)
        elif width < 1300:
            self.setSpacing(24)
            self.setContentsMargins(24, 24, 24, 24)
        else:
            self.setSpacing(32)
            self.setContentsMargins(40, 40, 40, 40)
