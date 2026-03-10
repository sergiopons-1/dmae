from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

CARD_COLOR    = "#0E4C66"   

def card_shadow(widget, blur=30, offset_y=6, opacity=50):
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, offset_y)
        shadow.setColor(QColor(0, 0, 0, opacity))
        widget.setGraphicsEffect(shadow)


class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setStyleSheet(f"""
            QFrame#Card {{
                background-color: {CARD_COLOR};
                border-radius: 16px;
                border: 1px solid #E0D8C8;
            }}
        """)
        card_shadow(self)   