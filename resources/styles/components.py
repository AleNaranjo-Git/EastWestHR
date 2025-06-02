from resources.styles.colors import *

# Input fields style
INPUT_STYLE = f"""
    QLineEdit {{
        border: none;
        border-bottom: 2px solid {SECONDARY_COLOR};
        padding: 8px 0;
        font-size: 12pt;
        color: {TEXT_COLOR};
        background: transparent;
    }}
    QLineEdit:focus {{
        border-bottom: 2px solid {PRIMARY_COLOR};
    }}
    QLineEdit::placeholder {{
        color: {TEXT_COLOR};
    }}
"""

# Button styles
BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 14pt;
    }}
    QPushButton:hover {{
        background-color: {PRIMARY_HOVER};
    }}
"""

# Title styles
TITLE_STYLE = f"""
    color: {PRIMARY_COLOR};
    font-size: 24pt;
"""

# Error label style
ERROR_LABEL_STYLE = f"""
    color: {ERROR_COLOR};
    font-size: 10pt;
"""