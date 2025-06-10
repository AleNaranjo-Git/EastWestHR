from db.connection import DatabaseConnection
import uuid
import logging

class PayrollType:
    def __init__(self, payroll_type_id: uuid.UUID, payroll_type_name: str):
        self.payroll_type_id = payroll_type_id
        self.payroll_type_name = payroll_type_name

    @classmethod
    def get_payroll_type_by_id(cls, payroll_type_id: str):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM payroll_type WHERE payroll_type_id = ?", payroll_type_id)
            row = cursor.fetchone()
            cursor.close()
            if row:
                logging.debug(f"PayrollType found with payroll_type_id: {payroll_type_id[:8]}...")
                return cls(
                    payroll_type_id=row[0],
                    payroll_type_name=row[1]
                )
            logging.warning(f"No payroll type found with payroll_type_id: {payroll_type_id[:8]}...")
            return None
        except Exception as e:
            logging.error(f"Error searching for payroll type by id: {e}")
            return None
        finally:
            conn.close()