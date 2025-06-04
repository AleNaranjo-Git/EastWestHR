from db.connection import DatabaseConnection
import uuid, datetime

class Employee:
    def __init__(
        self,
        employee_id: uuid.UUID,
        first_name: str,
        last_name_1: str,
        last_name_2: str,
        national_id: str,
        email: str,
        hire_date: datetime.date,
        birth_date: datetime.date,
        payroll_type_id: uuid.UUID,
        department_id: uuid.UUID,
        position_id: uuid.UUID,
        supervisor_id: uuid.UUID
    ):
        self.employee_id = employee_id
        self.first_name = first_name
        self.last_name_1 = last_name_1
        self.last_name_2 = last_name_2
        self.national_id = national_id
        self.email = email
        self.hire_date = hire_date
        self.birth_date = birth_date
        self.payroll_type_id = payroll_type_id
        self.department_id = department_id
        self.position_id = position_id
        self.supervisor_id = supervisor_id

    @classmethod
    def get_employee_by_national_id(cls, national_id: str):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employee WHERE national_id = ?", national_id)
            row = cursor.fetchone()
            cursor.close()
            if row:
                return cls(
                    employee_id=row[0],
                    first_name=row[1],
                    last_name_1=row[2],
                    last_name_2=row[3],
                    national_id=row[4],
                    email=row[5],
                    hire_date=row[6],
                    birth_date=row[7],
                    payroll_type_id=row[8],
                    department_id=row[9],
                    position_id=row[10],
                    supervisor_id=row[11]
                )
            return None
        except Exception as e:
            print(f"Error searching for employee: {e}")
            return None
        finally:
            conn.close()
            
    @classmethod
    def get_employee_by_id(cls, employee_id: str):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employee WHERE employee_id = ?", employee_id)
            row = cursor.fetchone()
            cursor.close()
            if row:
                return cls(
                    employee_id=row[0],
                    first_name=row[1],
                    last_name_1=row[2],
                    last_name_2=row[3],
                    national_id=row[4],
                    email=row[5],
                    hire_date=row[6],
                    birth_date=row[7],
                    payroll_type_id=row[8],
                    department_id=row[9],
                    position_id=row[10],
                    supervisor_id=row[11]
                )
            return None
        except Exception as e:
            print(f"Error searching for employee by id: {e}")
            return None
        finally:
            conn.close()

