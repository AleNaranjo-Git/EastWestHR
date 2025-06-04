from typing import Dict, cast
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from resources.styles.colors import SIDEBAR_BG
from resources.styles.components import SIDEBAR_BUTTON_STYLE

class MenuSidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self.setObjectName("Sidebar")

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(SIDEBAR_BG))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.setStyleSheet(SIDEBAR_BUTTON_STYLE)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 30, 10, 20)
        layout.setSpacing(10)
    
        self.buttons: Dict[str, QPushButton] = {}
        names = [
            ("Vacaciones", "Solicitar Vacación"),
            ("Permisos", "Solicitar Permiso"),
            ("Constancia", "Constancia Salarial"),
            ("FCL", "FCL"),
            ("Aprobar", "aprobar Solicitudes")
        ]

        for key, label in names:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setMinimumHeight(44)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch()
        self.setLayout(layout)

        self.buttons["Vacaciones"].setChecked(True)

        for btn in self.buttons.values():
            btn.clicked.connect(self._handle_button_checked)

    def _handle_button_checked(self):
        clicked_button = cast(QPushButton, self.sender())
        for btn in self.buttons.values():
            if btn != clicked_button:
                btn.setChecked(False)
        clicked_button.setChecked(True)
