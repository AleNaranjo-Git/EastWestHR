import logging
from db.connection import DatabaseConnection
from datetime import date
from typing import Optional

class Employee:
    def __init__(
        self,
        employee_id: Optional[int],
        last_name_1: str,
        last_name_2: str,
        first_name: str,
        national_id: str,
        department: str,
        position: str,
        hire_date: date,
        supervisor: str,
        email: str,
        birth_date: Optional[date]
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
        """
        Fetch an employee from VistaEmpleados2 by their national ID (cedula).
        """
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM VistaEmpleados2 WHERE cedula = ?",
                national_id
            )
            row = cursor.fetchone()
            cursor.close()
            if row:
                return Employee(
                    employee_id=None,
                    last_name_1=row[0].strip(),
                    last_name_2=row[1].strip(),
                    first_name=row[2].strip(),
                    national_id=row[3].strip(),
                    department=row[4],
                    position=row[5],
                    hire_date=row[6],
                    supervisor=row[7],
                    email=row[8].strip(),
                    birth_date=None
                )
            logging.warning(f"No employee found with national_id: {national_id[:8].strip()}...")
            return None
        except Exception as e:
            logging.error(f"Error searching for employee: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_full_name_by_national_id(national_id: str) -> Optional[str]:
        """
        Fetch the full name of an employee from VistaEmpleados2 by their national ID (cedula).
        """
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT RTRIM(nombre) + ' ' + RTRIM(apellidoPaterno) + ' ' + RTRIM(apellidoMaterno) AS full_name
                FROM VistaEmpleados2
                WHERE cedula = ?
                """,
                national_id
            )
            row = cursor.fetchone()
            cursor.close()
            if row:
                return row[0]
            logging.warning(f"No employee found with national_id: {national_id}.")
            return None
        except Exception as e:
            logging.error(f"Error fetching full name for national_id {national_id}: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_national_id_by_full_name(full_name: str) -> Optional[str]:
        """
        Fetch the national ID (cedula) of an employee from VistaEmpleados2 by their full name.
        """
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            name_parts = full_name.split()
            if len(name_parts) < 3:
                logging.error("Full name must include first name, last name, and second last name.")
                return None

            first_name = name_parts[0]
            last_name_1 = name_parts[1]
            last_name_2 = " ".join(name_parts[2:])

            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT cedula
                FROM VistaEmpleados2
                WHERE RTRIM(nombre) = ? AND RTRIM(apellidoPaterno) = ? AND RTRIM(apellidoMaterno) = ?
                """,
                (first_name, last_name_1, last_name_2)
            )
            row = cursor.fetchone()
            cursor.close()
            if row:
                return row[0]
            logging.warning(f"No employee found with full name: {full_name}.")
            return None
        except Exception as e:
            logging.error(f"Error fetching national ID for full name {full_name}: {e}")
            return None
        finally:
            conn.close()