from resources.styles.colors import *

# Input fields style
INPUT_STYLE = f"""
    QLineEdit {{
        border: none;
        border-bottom: 2px solid {SECONDARY_COLOR};
        padding: 6px 4px;
        font-size: 12pt;
        color: {SECONDARY_COLOR};
        background-color: {BACKGROUND};
    }}
    QLineEdit:focus {{
        border-bottom: 2px solid {PRIMARY_COLOR};
        outline: none;
    }}
    QLineEdit::placeholder {{
        color: {SECONDARY_COLOR};
        opacity: 0.6;
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
        height: 40px;
    }}
    QPushButton:hover {{
        background-color: {PRIMARY_HOVER};
    }}
"""

# Title styles
TITLE_STYLE = f"""
    color: {PRIMARY_COLOR};
    font-size: 24pt;
    font-weight: 600;
"""

# Error label style
ERROR_LABEL_STYLE = f"""
    color: {ERROR_COLOR};
    font-size: 10pt;
"""

SIDEBAR_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: transparent;
        color: {PRIMARY_COLOR};
        border: none;
        text-align: left;
        padding: 12px 20px;
        font-size: 13pt;
        border-radius: 12px;
    }}
    QPushButton:hover {{
        background-color: #5c6b73;
    }}
    QPushButton:checked {{
        background-color: {PRIMARY_COLOR};
        color: {BACKGROUND};
        font-weight: bold;
    }}
"""

LABEL_STYLE = """
    font-size: 13pt;
    color: #5c6068;
    padding-bottom: 2px;
    padding-right: 8px;
"""
DATE_EDIT_STYLE = f"""
    QDateEdit {{
        border: none;
        border-bottom: 2px solid {SECONDARY_COLOR};
        padding: 4px 4px;
        font-size: 12pt;
        color: {TEXT_COLOR};
        background-color: {BACKGROUND};
    }}
    QDateEdit:focus {{
        border-bottom: 2px solid {PRIMARY_COLOR};
        outline: none;
    }}
"""
COMBOBOX_STYLE = f"""
    QComboBox {{
        border: none;
        border-bottom: 2px solid {SECONDARY_COLOR};
        padding: 4px 4px;
        font-size: 12pt;
        color: {SECONDARY_COLOR};
        background-color: {BACKGROUND};
    }}
    QComboBox:focus {{
        border-bottom: 2px solid {PRIMARY_COLOR};
        outline: none;
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: none;
    }}
    QComboBox QAbstractItemView {{
        background-color: {BACKGROUND};
        selection-background-color: {PRIMARY_COLOR};
        color: {SECONDARY_COLOR};
    }}
"""

SEPARATOR_LINE_STYLE = f"""
    QFrame {{
        color: {SECONDARY_COLOR};
        background-color: {SECONDARY_COLOR};
        min-height: 2px;
        max-height: 2px;
        border: none;
    }}
"""

# Filter button style
FILTER_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
        font-size: 11pt;
    }}
    QPushButton:hover {{
        background-color: {PRIMARY_HOVER};
    }}
"""

CARD_STYLE = """
    QFrame {
        background-color: {BACKGROUND};
        border: none;
        border-radius: 8px;
    }
"""

INFO_CARD_STYLE = """
    QFrame {
        background-color: {BACKGROUND};
        border: none;
        border-radius: 8px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.05);
    }
"""

FILTER_TITLE_STYLE = f"font-weight: bold; font-size: 14px; color: {PRIMARY_COLOR};"

CLEAR_FILTERS_STYLE = f"""
    QPushButton {{
        background: transparent;
        border: none;
        color: {PRIMARY_COLOR};
        text-decoration: underline;
        font-size: 11pt;
    }}
    QPushButton:hover {{
        color: {PRIMARY_HOVER};
    }}
"""

REJECT_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {SECONDARY_COLOR};
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 14pt;
        height: 40px;
    }}
    QPushButton:hover {{
        background-color: #4c505a;
    }}
"""