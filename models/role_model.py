from db.connection import DatabaseConnection
import uuid
import logging

class Role:
    def __init__(self, role_id: uuid.UUID, role_name: str):
        self.role_id = role_id
        self.role_name = role_name

    @classmethod
    def get_role_by_id(cls, role_id: str):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM role WHERE role_id = ?", role_id)
            row = cursor.fetchone()
            cursor.close()
            if row:
                logging.debug(f"Role found with role_id: {role_id[:8]}...")
                return cls(
                    role_id=row[0],
                    role_name=row[1]
                )
            logging.warning(f"No role found with role_id: {role_id[:8]}...")
            return None
        except Exception as e:
            logging.error(f"Error searching for role by id: {e}")
            return None
        finally:
            conn.close()