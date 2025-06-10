from typing import List, Tuple, Optional
from datetime import date, timedelta
from models.employee_model import Employee
from models.vacation_request_model import VacationRequest
import holidays
import logging


class VacationsLogic:
    @staticmethod
    def get_months_worked(employee_id: str) -> int:
        employee = Employee.get_employee_by_id(employee_id)
        if not employee or not employee.hire_date:
            logging.warning(f"Employee not found or missing hire date for employee_id: {employee_id[:8]}...")
            return 0

        hire_date = employee.hire_date
        today = date.today()
        months = (today.year - hire_date.year) * 12 + (today.month - hire_date.month)
        if today.day < hire_date.day:
            months -= 1

        logging.debug(f"Months worked for employee_id {employee_id[:8]}...: {max(0, months)}")
        return max(0, months)
    
    @staticmethod
    def get_approved_vacation_days(employee_id: str) -> int:
        vacations = VacationRequest.get_vacations_by_employee_id(employee_id)
        total = 0
        for vac in vacations:
            if vac.status.lower() == "aprobado":
                total += vac.total_days
        logging.debug(f"Approved vacation days for employee_id {employee_id[:8]}...: {total}")
        return total
    
    @staticmethod
    def get_holidays(start_date: date, end_date: date, country: str = "CR") -> List[date]:
        holiday_dates: List[date] = []
        cr_holidays = holidays.country_holidays(country, years=range(start_date.year, end_date.year + 1))
        for single_date in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
            if single_date in cr_holidays:
                holiday_dates.append(single_date)
        logging.debug(f"Holidays between {start_date} and {end_date}: {holiday_dates}")
        return holiday_dates
    
    @staticmethod
    def is_business_day(check_date: date, holidays_list: List[date]) -> bool:
        is_business = check_date.weekday() < 5 and check_date not in holidays_list
        return is_business
    
    @staticmethod
    def get_business_days_in_range(start_date: date, end_date: date, country: str = "CR") -> List[date]:
        holidays_list = VacationsLogic.get_holidays(start_date, end_date, country)
        business_days: List[date] = []
        for n in range((end_date - start_date).days + 1):
            current = start_date + timedelta(days=n)
            if VacationsLogic.is_business_day(current, holidays_list):
                business_days.append(current)
        logging.debug(f"Business days between {start_date} and {end_date}: {len(business_days)}")
        return business_days
    
    @staticmethod
    def has_overlapping_vacation(employee_id: str, start_date: date, end_date: date) -> bool:
        """
        Returns True if the employee already has an approved or pending vacation overlapping with the given range.
        """
        vacations = VacationRequest.get_vacations_by_employee_id(employee_id)
        for vac in vacations:
            if vac.status.lower() in ("aprobado", "pendiente"):
                if start_date <= vac.end_date and end_date >= vac.start_date:
                    logging.debug(f"Overlapping vacation found for employee_id {employee_id[:8]}... in range {start_date} to {end_date}")
                    return True
        logging.debug(f"No overlapping vacation found for employee_id {employee_id[:8]}... in range {start_date} to {end_date}")
        return False
    
    @staticmethod
    def can_request_vacation(employee_id: str, start_date: date, end_date: date) -> Tuple[bool, str]:
        months_worked = VacationsLogic.get_months_worked(employee_id)
        approved_days = VacationsLogic.get_approved_vacation_days(employee_id)
        available_days = months_worked - approved_days

        requested_business_days = len(VacationsLogic.get_business_days_in_range(start_date, end_date))

        if VacationsLogic.has_overlapping_vacation(employee_id, start_date, end_date):
            logging.warning(f"Vacation request denied for employee_id {employee_id[:8]}...: overlapping vacation in range {start_date} to {end_date}")
            return False, "Ya existe una vacación aprobada o pendiente en ese rango."

        if start_date > end_date:
            logging.warning(f"Vacation request denied for employee_id {employee_id[:8]}...: start date after end date.")
            return False, "La fecha de inicio no puede ser posterior a la fecha final."
        if requested_business_days <= 0:
            logging.warning(f"Vacation request denied for employee_id {employee_id[:8]}...: no business days in range.")
            return False, "No hay días laborales en el rango seleccionado."
        if requested_business_days > available_days:
            logging.warning(f"Vacation request denied for employee_id {employee_id[:8]}...: not enough available days. Available: {available_days}, requested: {requested_business_days}")
            return False, f"No tiene suficientes días disponibles. Disponibles: {available_days}, solicitados: {requested_business_days}"

        logging.info(f"Vacation request approved for employee_id {employee_id[:8]}...: {requested_business_days} business days requested.")
        return True, ""

    @staticmethod
    def create_vacation_request(
        request_date: date,
        start_date: date,
        end_date: date,
        total_days: int,
        status: str,
        week_number: int,
        employee_id: str,
        approved_by_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Validates and creates a vacation request, saving it to the database.
        Returns (True, "") if created successfully, (False, reason) otherwise.
        """
        import uuid

        can_request, reason = VacationsLogic.can_request_vacation(employee_id, start_date, end_date)
        if not can_request:
            logging.warning(f"Vacation request denied for employee_id {employee_id[:8]}...: {reason}")
            return False, reason

        try:
            vacation = VacationRequest(
                request_date=request_date,
                start_date=start_date,
                end_date=end_date,
                total_days=total_days,
                status=status,
                week_number=week_number,
                employee_id=uuid.UUID(employee_id),
                approved_by_id=uuid.UUID(approved_by_id) if approved_by_id else None
            )
            result = vacation.save_vacation()
            if result:
                logging.info(
                    f"Vacation request created for employee_id {employee_id[:8]}... from {start_date} to {end_date}"
                )
                return True, ""
            else:
                return False, "Error al guardar la solicitud en la base de datos."
        except Exception as e:
            logging.error(
                f"Error creating vacation request for employee_id {employee_id[:8]}...: {e}"
            )
            return False, "Error interno al crear la solicitud."