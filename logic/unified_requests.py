from datetime import date
from typing import List, Dict, Any, Optional
from logic.permits_logic import PermitsLogic
from models.vacation_request_model import VacationRequest
from models.permit_request_model import PermitRequest
from models.employee_model import Employee
from models.permit_type_model import PermitType

class UnifiedRequest:
    def __init__(
        self,
        type_: str,  # "Permiso" or "Vacacion"
        permit_type_name: str,
        employee_name: str,
        employee_national_id: str,
        request_date: date,
        start_date: date,
        end_date: date,
        check_in_time: Optional[str],
        check_out_time: Optional[str],
        total_days: int,
        status: str,
        week_number: int,
        request_id: int,
        supervisor_name: Optional[str] = None
    ):
        self.type_ = type_
        self.permit_type_name = permit_type_name
        self.employee_name = employee_name
        self.employee_national_id = employee_national_id
        self.request_date = request_date
        self.start_date = start_date
        self.end_date = end_date
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.total_days = total_days
        self.status = status
        self.week_number = week_number
        self.request_id = request_id
        self.supervisor_name = supervisor_name

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type_,
            "permit_type_name": self.permit_type_name,
            "employee_name": self.employee_name,
            "employee_national_id": self.employee_national_id,
            "request_date": self.request_date,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "check_in_time": self.check_in_time,
            "check_out_time": self.check_out_time,
            "total_days": self.total_days,
            "status": self.status,
            "week_number": self.week_number
        }

def get_unified_requests_by_supervisor(supervisor_national_id: str) -> List[UnifiedRequest]:
    unified_requests: List[UnifiedRequest] = []

    # Get permits
    permits = PermitsLogic.get_permit_full_info_by_supervisor_id(supervisor_national_id)
    for permit in permits:
        employee = Employee.get_employee_by_national_id(permit["employee_national_id"])
        employee_name = (
            f"{employee.first_name.strip()} {employee.last_name_1.strip()} {employee.last_name_2.strip()}"
            if employee else permit["employee_national_id"]
        )
        unified_requests.append(UnifiedRequest(
            type_="Permiso",
            permit_type_name=permit["permit_type_name"],
            employee_name=employee_name,
            employee_national_id=permit["employee_national_id"].strip(),
            request_date=permit["request_date"],
            start_date=permit["absence_date"],
            end_date=permit["absence_date"],
            check_in_time=str(permit["check_in_time"]),
            check_out_time=str(permit["check_out_time"]),
            total_days=1,
            status=permit["status"],
            week_number=permit["week_number"],
            request_id=permit["permit_request_id"]
        ))

    # Get vacations
    vacations = VacationRequest.get_vacations_by_supervisor_id(supervisor_national_id)
    for vac in vacations:
        employee = Employee.get_employee_by_national_id(vac.employee_national_id)
        employee_name = (
            f"{employee.first_name.strip()} {employee.last_name_1.strip()} {employee.last_name_2.strip()}"
            if employee else vac.employee_national_id
        )
        unified_requests.append(UnifiedRequest(
            type_="Vacacion",
            permit_type_name="-",
            employee_name=employee_name,
            employee_national_id=vac.employee_national_id.strip(),
            request_date=vac.request_date,
            start_date=vac.start_date,
            end_date=vac.end_date,
            check_in_time="-",
            check_out_time="-",
            total_days=vac.total_days,
            status=vac.status,
            week_number=vac.week_number,
            request_id=vac.vacation_request_id
        ))

    return unified_requests

def get_all_unified_requests_ordered() -> List[UnifiedRequest]:
    unified_requests: List[UnifiedRequest] = []

    # Get permits
    permits = PermitRequest.get_all_permit_requests_ordered()
    for permit in permits:
        employee = Employee.get_employee_by_national_id(permit.employee_national_id)
        employee_name = (
            f"{employee.first_name.strip()} {employee.last_name_1.strip()} {employee.last_name_2.strip()}"
            if employee else permit.employee_national_id
        )
        
        supervisor = Employee.get_employee_by_national_id(permit.approver_national_id) if permit.approver_national_id else None
        supervisor_name = (
            f"{supervisor.first_name.strip()} {supervisor.last_name_1.strip()} {supervisor.last_name_2.strip()}"
            if supervisor else None
        )
        
        permit_type = PermitType.get_permit_type_by_id(permit.permit_type_id)
        permit_type_name = (
            permit_type.permit_type_name if permit_type else "Desconocido"
        )
        
        unified_requests.append(UnifiedRequest(
            type_="Permiso",
            permit_type_name=permit_type_name,
            employee_name=employee_name,
            employee_national_id=permit.employee_national_id.strip(),
            request_date=permit.request_date,
            start_date=permit.absence_date,
            end_date=permit.absence_date,
            check_in_time=str(permit.check_in_time),
            check_out_time=str(permit.check_out_time),
            total_days=1,
            status=permit.status,
            week_number=permit.week_number,
            request_id=permit.permit_request_id,
            supervisor_name=supervisor_name
        ))

    # Get vacations
    vacations = VacationRequest.get_all_vacation_requests_ordered()
    for vac in vacations:
        employee = Employee.get_employee_by_national_id(vac.employee_national_id)
        employee_name = (
            f"{employee.first_name.strip()} {employee.last_name_1.strip()} {employee.last_name_2.strip()}"
            if employee else vac.employee_national_id
        )
        
        supervisor = Employee.get_employee_by_national_id(vac.approver_national_id) if vac.approver_national_id else None
        supervisor_name = (
            f"{supervisor.first_name.strip()} {supervisor.last_name_1.strip()} {supervisor.last_name_2.strip()}"
            if supervisor else None
        )
        unified_requests.append(UnifiedRequest(
            type_="Vacacion",
            permit_type_name="-",
            employee_name=employee_name,
            employee_national_id=vac.employee_national_id.strip(),
            request_date=vac.request_date,
            start_date=vac.start_date,
            end_date=vac.end_date,
            check_in_time="-",
            check_out_time="-",
            total_days=vac.total_days,
            status=vac.status,
            week_number=vac.week_number,
            request_id=vac.vacation_request_id,
            supervisor_name=supervisor_name
        ))

    # Sort unified requests by status
    unified_requests.sort(key=lambda req: {
        "Pendiente": 1,
        "Aprobado": 2,
        "Denegado": 3
    }.get(req.status, 4))
    
    return unified_requests

