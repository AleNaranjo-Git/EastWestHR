from db.connection import DatabaseConnection
import uuid

class Role:
    def __init__(self, role_id: uuid.UUID, role_name: str):
        self.role_id = role_id
        self.role_name = role_name

    @classmethod
    def get_role_by_id(cls, role_id: str):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM role WHERE role_id = ?", role_id)
            row = cursor.fetchone()
            cursor.close()
            if row:
                return cls(
                    role_id=row[0],
                    role_name=row[1]
                )
            return None
        except Exception as e:
            print(f"Error searching for role by id: {e}")
            return None
        finally:
            conn.close()