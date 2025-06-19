from typing import Literal, Optional, Dict, Any
import bcrypt
import logging
from db.connection import DatabaseConnection

AuthResult = Literal["success", "connection_error", "invalid_user", "invalid_password"]

class Session:
    current_user: Optional[Dict[str, Any]] = None

def authenticate(email: str, password: str) -> AuthResult:
    db = DatabaseConnection()
    conn = db.connect()
    
    if not conn:
        logging.error("Database connection error during authentication.")
        return "connection_error"

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT idUsuario, correologin, contrasenahash, cedulaEmpleado, idRol
            FROM usuario
            WHERE correologin = ?
        """, (email,))
        
        result = cursor.fetchone()
        if not result:
            logging.warning(f"Authentication failed: invalid user '{email}'.")
            return "invalid_user"

        idUsuario, correologin, hashed_pw, cedulaEmpleado, idRol = result

        if not bcrypt.checkpw(password.encode('utf-8'), hashed_pw.encode('utf-8')):
            logging.warning(f"Authentication failed: invalid password for user '{email}'.")
            return "invalid_password"

        # Store session info
        Session.current_user = {
            "idUsuario": idUsuario,
            "correoLogin": correologin,
            "cedulaEmpleado": cedulaEmpleado,
            "idRol": idRol
        }

        logging.info(f"User '{email}' authenticated successfully.")
        return "success"

    except Exception as e:
        logging.error(f"Authentication error for user '{email}': {str(e)}")
        return "connection_error"
    finally:
        db.close()

def logout():
    Session.current_user = None

def get_current_user() -> Optional[Dict[str, Any]]:
    return Session.current_user

def get_current_user_role() -> Optional[int]:
    if Session.current_user:
        return Session.current_user.get("idRol")
    return None

def get_current_user_national_id() -> Optional[str]:
    if Session.current_user:
        return Session.current_user.get("cedulaEmpleado")
    return None