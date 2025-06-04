from db.connection import DatabaseConnection
import uuid

class Department:
    def __init__(self, department_id: uuid.UUID, department_name: str):
        self.department_id = department_id
        self.department_name = department_name

    @classmethod
    def get_deparment_by_id(cls, department_id: str):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM department WHERE department_id = ?", department_id)
            row = cursor.fetchone()
            cursor.close()
            if row:
                return cls(
                    department_id=row[0],
                    department_name=row[1]
                )
            return None
        except Exception as e:
            print(f"Error searching for department by id: {e}")
            return None
        finally:
            conn.close()