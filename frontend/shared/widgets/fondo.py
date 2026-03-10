from PyQt6.QtWidgets import QWidget

BG_COLOR = "#FFF7E7" 
BLUE_COLOR = "#0E4C66"

class BeigeBg(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        self.resize(1000, 800)

class BlueBg(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {BLUE_COLOR};")
        