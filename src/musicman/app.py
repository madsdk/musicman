"""QApplication setup."""

from PySide6.QtWidgets import QApplication

from musicman.ui.main_window import MainWindow


def create_app() -> QApplication:
    app = QApplication([])
    app.setApplicationName("MusicMan")
    app.setOrganizationName("MusicMan")

    window = MainWindow()
    window.show()

    # Keep a reference so the window isn't garbage collected
    app._main_window = window

    return app
