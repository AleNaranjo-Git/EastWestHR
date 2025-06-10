from db.connection import DatabaseConnection
import uuid
import logging

class Department:
    def __init__(self, department_id: uuid.UUID, department_name: str):
        self.department_id = department_id
        self.department_name = department_name

    @classmethod
    def get_deparment_by_id(cls, department_id: str):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM department WHERE department_id = ?", department_id)
            row = cursor.fetchone()
            cursor.close()
            if row:
                logging.debug(f"Department found with department_id: {department_id[:8]}...")
                return cls(
                    department_id=row[0],
                    department_name=row[1]
                )
            logging.warning(f"No department found with department_id: {department_id[:8]}...")
            return None
        except Exception as e:
            logging.error(f"Error searching for department by id: {e}")
            return None
        finally:
            conn.close()