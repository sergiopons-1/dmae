import sys
from PyQt6.QtWidgets import (QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

PRIMARY          = "#0E4C66"  
PRIMARY_HOVER    = "#1878A1"
PRIMARY_PRESSED  = "#0F3F3F"

class PrimaryButton(QPushButton):
    def __init__(self, text: str, tamano: int=20, accion=None, parent=None):
        super().__init__(str(text).upper(), parent)
        self.setMinimumHeight(60)
        self.setMaximumSize(350, 60)
        self.setFixedSize(350,60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setFont(QFont("Segoe UI", tamano, QFont.Weight.Bold))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 28px;
                letter-spacing: 1px;
                text-align: center;
            }}
            QPushButton:hover {{ background-color: {PRIMARY_HOVER}; }}
            QPushButton:pressed {{ background-color: {PRIMARY_PRESSED}; }}
        """)

        if accion is not None:
            self.clicked.connect(accion)


class SidebarButton(QPushButton):
    def __init__(self, text: str, tamano: int=20, accion=None, parent=None):
        super().__init__(str(text).upper(), parent)
        self.setMinimumHeight(60)
        self.setBaseSize(350, 60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI", tamano, QFont.Weight.Bold))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                border: none;
                border-radius: 0px;
                padding: 16px 20px;
                text-align: left;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {PRIMARY_HOVER}; }}
            QPushButton:pressed {{ background-color: {PRIMARY_PRESSED}; }}
        """)

        if accion is not None:
            self.clicked.connect(accion)

class PaginationButton(QPushButton):

    def __init__(self, label: str, action=None, parent=None):
        super().__init__(label, parent)
        self.setFixedSize(36, 36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(self._estilo_pag_btn())

        if action is not None:
            self.clicked.connect(action)

    def _estilo_pag_btn(self) -> str:
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {PRIMARY};
                border: none;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ color: #1878A1; }}
            QPushButton:disabled {{ color: #C0C0C0; }}
        """


class BackButton(QPushButton):
    def __init__(self, text: str = "Volver", tamano: int = 24, accion=None, parent=None):
        super().__init__(f"← {text}", parent)
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI", tamano, QFont.Weight.Bold))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {PRIMARY};
                border: none;
                padding: 6px 10px;
                text-align: left;
                font-size: 14px;
            }}
            QPushButton:hover {{ color: {PRIMARY_HOVER}; }}
            QPushButton:pressed {{ color: {PRIMARY_PRESSED}; }}
        """)

        if accion is not None:
            self.clicked.connect(accion)