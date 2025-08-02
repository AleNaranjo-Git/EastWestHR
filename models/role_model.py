from db.connection import DatabaseConnection
import logging
from typing import Optional

class Role:
    def __init__(self, role_id: int, role_name: str):
        self.role_id = role_id
        self.role_name = role_name

    @classmethod
    def get_role_by_id(cls, role_id: int):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Rol WHERE idRol = ?", role_id)
            row = cursor.fetchone()
            cursor.close()
            if row:
                logging.debug(f"Role found with role_id: {role_id}")
                return cls(
                    role_id=row[0],
                    role_name=row[1]
                )
            logging.warning(f"No role found with role_id: {role_id}")
            return None
        except Exception as e:
            logging.error(f"Error searching for role by id: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def get_role_id_by_name(cls, role_name: str) -> Optional[int]:
        """Fetch the role ID by its name."""
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT idRol FROM Rol WHERE nombreRol = ?", (role_name,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                logging.debug(f"Role ID found for role name '{role_name}': {row[0]}")
                return row[0]
            logging.warning(f"No role ID found for role name: {role_name}")
            return None
        except Exception as e:
            logging.error(f"Error fetching role ID by name: {e}")
            return None
        finally:
            conn.close()