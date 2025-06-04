from models.employee_model import Employee
from models.deparment_model import Department
from models.position_model import Position
from models.payroll_type_model import PayrollType
from typing import Optional, Dict, Any

class EmployeeLogic:
    @staticmethod
    def get_employee_full_info_by_national_id(national_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns all employee info with names instead of IDs, given a national_id.
        """
        employee = Employee.get_employee_by_national_id(national_id)
        if not employee:
            return None

        department = Department.get_deparment_by_id(str(employee.department_id)) if employee.department_id else None
        position = Position.get_position_by_id(str(employee.position_id)) if employee.position_id else None
        payroll_type = PayrollType.get_payroll_type_by_id(str(employee.payroll_type_id)) if employee.payroll_type_id else None
        supervisor = Employee.get_employee_by_id(str(employee.supervisor_id)) if employee.supervisor_id else None

        return {
            "employee_id": str(employee.employee_id),
            "first_name": employee.first_name,
            "last_name_1": employee.last_name_1,
            "last_name_2": employee.last_name_2,
            "national_id": employee.national_id,
            "email": employee.email,
            "hire_date": employee.hire_date,
            "birth_date": employee.birth_date,
            "payroll_type": payroll_type.payroll_type_name if payroll_type else None,
            "department": department.department_name if department else None,
            "position": position.position_name if position else None,
            "supervisor": (
                f"{supervisor.first_name} {supervisor.last_name_1} {supervisor.last_name_2}"
                if supervisor else None
            ),
            "supervisor_id": str(employee.supervisor_id) if employee.supervisor_id else None
        }