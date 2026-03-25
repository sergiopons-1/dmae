from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class MiProgreso(QWidget):
    def __init__(self, router):
        super().__init__()
        self.router = router
        
        layout = QVBoxLayout(self)
        label = QLabel("Mi Progreso")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)