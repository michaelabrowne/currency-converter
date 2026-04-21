"""Entry point — construct MVC triad and start the event loop."""
import sys

from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QApplication

from controller import AppController
from model import CurrencyModel
from view import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Currency Converter")
    QLocale.setDefault(QLocale.system())  # ensure system() is consistent with default

    model = CurrencyModel()
    view = MainWindow()
    app._controller = AppController(model, view)

    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
