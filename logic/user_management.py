import bcrypt
import logging
from db.connection import DatabaseConnection
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class User:
    def __init__(self, correo_login: str, cedula_empleado: str, id_rol: int):
        self.correo_login = correo_login
        self.cedula_empleado = cedula_empleado
        self.id_rol = id_rol

def get_all_users() -> List[User]:
    """Fetch all users with role names from the database."""
    db = DatabaseConnection()
    conn = db.get_connection("main")
    if conn is None:
        logging.error("Database connection failed.")
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.correoLogin, u.cedulaEmpleado, r.nombreRol
            FROM usuario u
            INNER JOIN Rol r ON u.idRol = r.idRol
            ORDER BY u.correoLogin ASC
        """)
        users = [
            User(
                correo_login=row[0],
                cedula_empleado=row[1].strip(),
                id_rol=row[2]
            )
            for row in cursor.fetchall()
        ]
        return users
    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        return []
    finally:
        if conn:
            db.close_connection("main")


def create_user(correo_login: str, password: str, cedula_empleado: str, role_name: str) -> Tuple[bool, str]:
    """Create a new user."""
    db = DatabaseConnection()
    conn = db.get_connection("main")
    if conn is None:
        logging.error("Database connection failed.")
        return False, "Error de conexión con la base de datos."

    try:
        cursor = conn.cursor()

        # Fetch the role ID by name
        from models.role_model import Role
        id_rol = Role.get_role_id_by_name(role_name)
        if id_rol is None:
            return False, f"Role '{role_name}' does not exist."

        # Check if user already exists
        cursor.execute("SELECT correoLogin FROM usuario WHERE correoLogin = ?", (correo_login,))
        if cursor.fetchone():
            return False, "User with this email already exists."

        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert the user
        cursor.execute("""
            INSERT INTO usuario (correoLogin, contrasenaHash, cedulaEmpleado, idRol)
            VALUES (?, ?, ?, ?)
        """, (correo_login, password_hash, cedula_empleado, id_rol))
        conn.commit()
        return True, "Usuario creado con éxito."
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        return False, f"Error: {str(e)}"
    finally:
        if conn:
            db.close_connection("main")


def reset_password(correo_login: str, new_password: str) -> Tuple[bool, str]:
    """Reset a user's password."""
    db = DatabaseConnection()
    conn = db.get_connection("main")
    if conn is None:
        logging.error("Database connection failed.")
        return False, "Error de conexión con la base de datos."

    try:
        cursor = conn.cursor()

        # Hash the new password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Update the password
        cursor.execute("""
            UPDATE usuario 
            SET contrasenaHash = ?
            WHERE correoLogin = ?
        """, (password_hash, correo_login))
        conn.commit()
        return True, "Contraseña restablecida con éxito."
    except Exception as e:
        logging.error(f"Error resetting password: {e}")
        return False, f"Error: {str(e)}"
    finally:
        if conn:
            db.close_connection("main")