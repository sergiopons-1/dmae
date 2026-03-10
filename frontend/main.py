import sys
from PyQt6.QtWidgets import QApplication
from auth.initial_window import InitialWindow
from shared.router import Router

class App:
    def __init__(self):
        self.router = Router()

    def run(self):
        self.router.show()

def main():
    app = QApplication(sys.argv)
    application = App()
    application.run()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()