import logging
from db.connection import DatabaseConnection
from datetime import date

class Employee:
    def __init__(
        self,
        employee_id: int,
        last_name_1: str,
        last_name_2: str,
        first_name: str,
        national_id: str,
        department: str,
        position: str,
        hire_date: date,
        supervisor: str,
        email: str,
        birth_date: date
    ):
        self.employee_id = employee_id
        self.last_name_1 = last_name_1
        self.last_name_2 = last_name_2
        self.first_name = first_name
        self.national_id = national_id
        self.department = department
        self.position = position
        self.hire_date = hire_date
        self.supervisor = supervisor
        self.email = email
        self.birth_date = birth_date

    @staticmethod
    def get_employee_by_national_id(national_id: str):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM VistaEmpleados WHERE cedula = ?",
                national_id
            )
            row = cursor.fetchone()
            cursor.close()
            if row:
                logging.debug(f"Employee found with national_id: {national_id}")
                return Employee(
                    employee_id=row[0],
                    last_name_1=row[1],
                    last_name_2=row[2],
                    first_name=row[3],
                    national_id=row[4],
                    department=row[5],
                    position=row[6],
                    hire_date=row[7],
                    supervisor=row[8],
                    email=row[9],
                    birth_date=row[10]
                )
            logging.warning(f"No employee found with national_id: {national_id[:8]}...")
            return None
        except Exception as e:
            logging.error(f"Error searching for employee: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_employee_by_id(employee_id: int):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM VistaEmpleados WHERE idEmpleado = ?",
                employee_id
            )
            row = cursor.fetchone()
            cursor.close()
            if row:
                logging.debug(f"Employee found with employee_id: {employee_id}")
                return Employee(
                    employee_id=row[0],
                    last_name_1=row[1],
                    last_name_2=row[2],
                    first_name=row[3],
                    national_id=row[4],
                    department=row[5],
                    position=row[6],
                    hire_date=row[7],
                    supervisor=row[8],
                    email=row[9],
                    birth_date=row[10]
                )
            logging.warning(f"No employee found with employee_id: {employee_id}")
            return None
        except Exception as e:
            logging.error(f"Error searching for employee by id: {e}")
            return None
        finally:
            conn.close()
