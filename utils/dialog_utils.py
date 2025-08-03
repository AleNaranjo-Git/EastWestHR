from PySide6.QtWidgets import QMessageBox, QWidget
from resources.styles.components import MESSAGE_BOX_STYLE

def show_information_dialog(parent: QWidget, title: str, message: str) -> None:
    """Show an information dialog."""
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    dialog.setIcon(QMessageBox.Icon.Information)
    dialog.setStyleSheet(MESSAGE_BOX_STYLE)
    dialog.exec()

def show_warning_dialog(parent: QWidget, title: str, message: str) -> None:
    """Show a warning dialog."""
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    dialog.setIcon(QMessageBox.Icon.Warning)
    dialog.setStyleSheet(MESSAGE_BOX_STYLE)
    dialog.exec()

def show_critical_dialog(parent: QWidget, title: str, message: str) -> None:
    """Show a critical dialog."""
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setStyleSheet(MESSAGE_BOX_STYLE)
    dialog.exec()