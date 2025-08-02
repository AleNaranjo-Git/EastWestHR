from models.employee_model import Employee
from typing import Optional, Dict, Any
import logging

class EmployeeLogic:
    @staticmethod
    def get_employee_full_info_by_national_id(national_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns all employee info with names instead of IDs, given a national_id.
        """
        employee = Employee.get_employee_by_national_id(national_id)
        if not employee:
            logging.warning(f"No employee found with national_id: {national_id.strip()}")
            return None

        supervisor = Employee.get_national_id_by_full_name(employee.supervisor) if employee.supervisor else None
        
        return {
            "employee_id": str(employee.employee_id),
            "first_name": employee.first_name,
            "last_name_1": employee.last_name_1,
            "last_name_2": employee.last_name_2,
            "national_id": employee.national_id,
            "email": employee.email,
            "hire_date": employee.hire_date,
            "department": employee.department,
            "position": employee.position,
            "supervisor": employee.supervisor,
            "supervisor_id": str(supervisor) if supervisor else None,
            "birth_date": employee.birth_date
        }