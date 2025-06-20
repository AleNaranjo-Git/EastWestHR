from typing import List, Tuple, Optional
from datetime import date, timedelta
from models.employee_model import Employee
from models.vacation_request_model import VacationRequest
import logging
from logic.date_logic import get_holidays, is_business_day

class VacationsLogic:
    @staticmethod
    def get_months_worked(employee_national_id: str) -> int:
        employee = Employee.get_employee_by_national_id(employee_national_id)
        if not employee or not employee.hire_date:
            logging.warning(f"Employee not found or missing hire date for national_id: {employee_national_id}")
            return 0

        hire_date = employee.hire_date
        today = date.today()
        months = (today.year - hire_date.year) * 12 + (today.month - hire_date.month)
        if today.day < hire_date.day:
            months -= 1

        logging.debug(f"Months worked for national_id {employee_national_id}: {max(0, months)}")
        return max(0, months)
    
    @staticmethod
    def get_approved_vacation_days(employee_national_id: str) -> int:
        vacations = VacationRequest.get_vacations_by_employee_national_id(employee_national_id)
        total = 0
        for vac in vacations:
            if vac.status.lower() == "aprobado":
                total += vac.total_days
        logging.debug(f"Approved vacation days for national_id {employee_national_id}: {total}")
        return total
    
    @staticmethod
    def get_pending_vacation_days(employee_national_id: str) -> int:
        vacations = VacationRequest.get_vacations_by_employee_national_id(employee_national_id)
        total = 0
        for vac in vacations:
            if vac.status.lower() == "pendiente":
                total += vac.total_days
        logging.debug(f"Pending vacation days for national_id {employee_national_id}: {total}")
        return total
    
    @staticmethod
    def get_business_days_in_range(start_date: date, end_date: date, country: str = "CR") -> List[date]:
        holidays_list = get_holidays(start_date, end_date, country)
        business_days: List[date] = []
        for n in range((end_date - start_date).days + 1):
            current = start_date + timedelta(days=n)
            if is_business_day(current, holidays_list):
                business_days.append(current)
        logging.debug(f"Business days between {start_date} and {end_date}: {len(business_days)}")
        return business_days
    
    @staticmethod
    def has_overlapping_vacation(employee_national_id: str, start_date: date, end_date: date) -> bool:
        """
        Returns True if the employee already has an approved or pending vacation overlapping with the given range.
        """
        vacations = VacationRequest.get_vacations_by_employee_national_id(employee_national_id)
        for vac in vacations:
            if vac.status.lower() in ("aprobado", "pendiente"):
                if start_date <= vac.end_date and end_date >= vac.start_date:
                    logging.debug(f"Overlapping vacation found for national_id {employee_national_id} in range {start_date} to {end_date}")
                    return True
        logging.debug(f"No overlapping vacation found for national_id {employee_national_id} in range {start_date} to {end_date}")
        return False
    
    @staticmethod
    def has_overlapping_permit_for_vacation(employee_national_id: str, start_date: date, end_date: date) -> bool:
        """
        Returns True if the employee has an approved or pending permit on any day in the vacation range.
        """
        from models.permit_request_model import PermitRequest
        permits = PermitRequest.get_permits_by_employee_national_id(employee_national_id)
        for permit in permits:
            if permit.status.lower() in ("aprobado", "pendiente"):
                if start_date <= permit.absence_date <= end_date:
                    logging.debug(f"Overlapping permit found for national_id {employee_national_id} on {permit.absence_date} in range {start_date} to {end_date}")
                    return True
        logging.debug(f"No overlapping permit found for national_id {employee_national_id} in range {start_date} to {end_date}")
        return False
    
    @staticmethod
    def can_request_vacation(employee_national_id: str, start_date: date, end_date: date) -> Tuple[bool, str]:
        months_worked = VacationsLogic.get_months_worked(employee_national_id)
        approved_days = VacationsLogic.get_approved_vacation_days(employee_national_id)
        pending_days = VacationsLogic.get_pending_vacation_days(employee_national_id)
        available_days = months_worked - approved_days - pending_days

        requested_business_days = len(VacationsLogic.get_business_days_in_range(start_date, end_date))

        if VacationsLogic.has_overlapping_vacation(employee_national_id, start_date, end_date):
            logging.warning(f"Vacation request denied for national_id {employee_national_id}: overlapping vacation in range {start_date} to {end_date}")
            return False, "Ya existe una vacación aprobada o pendiente en ese rango."
        
        if VacationsLogic.has_overlapping_permit_for_vacation(employee_national_id, start_date, end_date):
            logging.warning(f"Vacation request denied for national_id {employee_national_id}: overlapping permit in range {start_date} to {end_date}")
            return False, "Ya existe un permiso aprobado o pendiente en ese rango."

        if start_date > end_date:
            logging.warning(f"Vacation request denied for national_id {employee_national_id}: start date after end date.")
            return False, "La fecha de inicio no puede ser posterior a la fecha final."
        if requested_business_days <= 0:
            logging.warning(f"Vacation request denied for national_id {employee_national_id}: no business days in range.")
            return False, "No hay días laborales en el rango seleccionado."
        if requested_business_days > available_days:
            logging.warning(f"Vacation request denied for national_id {employee_national_id}: not enough available days. Available: {available_days}, requested: {requested_business_days}")
            return False, f"No tiene suficientes días disponibles. Disponibles: {available_days}, solicitados: {requested_business_days}"

        logging.info(f"Vacation request approved for national_id {employee_national_id}: {requested_business_days} business days requested.")
        return True, ""

    @staticmethod
    def create_vacation_request(
        request_date: date,
        start_date: date,
        end_date: date,
        total_days: int,
        status: str,
        week_number: int,
        employee_national_id: str,
        approver_national_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Validates and creates a vacation request, saving it to the database.
        Returns (True, "") if created successfully, (False, reason) otherwise.
        """
        can_request, reason = VacationsLogic.can_request_vacation(employee_national_id, start_date, end_date)
        if not can_request:
            logging.warning(f"Vacation request denied for national_id {employee_national_id}: {reason}")
            return False, reason

        try:
            result = VacationRequest.save_vacation(
                request_date=request_date,
                start_date=start_date,
                end_date=end_date,
                total_days=total_days,
                status=status,
                week_number=week_number,
                employee_national_id=employee_national_id,
                approver_national_id=approver_national_id
            )
            if result:
                logging.info(
                    f"Vacation request created for national_id {employee_national_id} from {start_date} to {end_date}"
                )
                return True, ""
            else:
                return False, "Error al guardar la solicitud en la base de datos."
        except Exception as e:
            logging.error(
                f"Error creating vacation request for national_id {employee_national_id}: {e}"
            )
            return False, "Error interno al crear la solicitud."