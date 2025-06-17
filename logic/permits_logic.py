from logic.vacations_logic import VacationsLogic
from logic.date_logic import get_holidays, is_business_day
from datetime import date, time
from models.permit_request_model import PermitRequest
from models.birthday_policy_model import BirthdayPolicy
from models.employee_model import Employee
from models.permit_type_model import PermitType
import logging
from typing import Tuple

class PermitsLogic:
    @staticmethod
    def get_available_vacation_days(employee_national_id: str) -> int:
        """
        Returns the number of vacation days the employee has available.
        """
        months_worked = VacationsLogic.get_months_worked(employee_national_id)
        approved_days = VacationsLogic.get_approved_vacation_days(employee_national_id)
        pending_days = VacationsLogic.get_pending_vacation_days(employee_national_id)
        return months_worked - approved_days - pending_days

    @staticmethod
    def is_permit_date_business_day(absence_date: date, country: str = "CR") -> Tuple[bool, str]:
        """
        Returns True if the absence_date is a business day (not weekend or holiday).
        """
        holidays_list = get_holidays(absence_date, absence_date, country)
        if is_business_day(absence_date, holidays_list):
            return True, ""
        else:
            return False, "La fecha seleccionada no es un día hábil."

    @staticmethod
    def has_overlapping_permit(employee_national_id: str, absence_date: date) -> Tuple[bool, str]:
        """
        Returns True if the employee already has an approved or pending permit on the given absence_date.
        """
        permits = PermitRequest.get_permits_by_employee_national_id(employee_national_id)
        for permit in permits:
            if permit.status.lower() in ("aprobado", "pendiente"):
                if permit.absence_date == absence_date:
                    logging.debug(
                        f"Overlapping permit found for national_id {employee_national_id} on {absence_date}"
                    )
                    return True, "Ya existe un permiso aprobado o pendiente para esa fecha."
        logging.debug(
            f"No overlapping permit found for national_id {employee_national_id} on {absence_date}"
        )
        return False, ""

    @staticmethod
    def validate_birthday_benefit(employee_national_id: str, selected_date: date) -> Tuple[bool, str]:
        """
        Checks if the employee can request a birthday leave on any day of their birthday month.
        Now allows any day in the birthday month, and checks for both approved and pending requests.
        """
        employee = Employee.get_employee_by_national_id(employee_national_id)
        assert employee is not None, "Employee existence should be validated in validate_generic_permit"

        policies = BirthdayPolicy.get_all_active_birthday_policies()
        if not policies:
            logging.warning("No active birthday policy found.")
            return False, "No hay política de cumpleaños activa."
        policy = policies[0]

        # Dynamic target group validation
        from models.target_group_model import TargetGroup
        target_group = TargetGroup.get_target_group_by_id(policy.target_group_id)
        target_group_name = target_group.target_group_name.lower() if target_group else ""

        # If the target group is not "todos", validate employee belongs to that group
        if target_group_name != "todos":
            employee_payroll_type = getattr(employee, "payroll_type", "").lower()
            if not (employee_payroll_type == target_group_name):
                logging.info(
                    f"Employee {employee_national_id} does not belong to target group '{target_group_name}'. Payroll type: {employee_payroll_type}"
                )
                return False, f"Solo personal {target_group_name} puede solicitar este permiso."

        # Allow any day in the birthday month
        birthday = employee.birth_date
        if birthday.month != selected_date.month:
            return False, "Solo puedes solicitar el permiso de cumpleaños en el mes de tu cumpleaños."

        # Check if already has a pending or approved birthday permit this year
        permits = PermitRequest.get_permits_by_employee_national_id(employee_national_id)
        for permit in permits:
            permit_type = PermitType.get_permit_type_by_id(permit.permit_type_id)
            if (
                permit_type and
                permit_type.permit_type_name.lower() == "beneficio cumpleaños" and
                permit.absence_date.year == selected_date.year and
                permit.status.lower() in ("aprobado", "pendiente")
            ):
                logging.info(f"Employee {employee_national_id} already has a pending or approved birthday leave for year {selected_date.year}.")
                return False, "Ya has solicitado o tienes aprobado el permiso de cumpleaños este año."

        logging.info(f"Birthday leave validated for employee {employee_national_id} on {selected_date}.")
        return True, "Permiso de cumpleaños válido."

    @staticmethod
    def validate_experience_years_benefit(employee_national_id: str, selected_date: date) -> Tuple[bool, str]:
        """
        Validates if the employee can request an experience years benefit on the selected date,
        according to all active experience years policies and business rules.
        """
        employee = Employee.get_employee_by_national_id(employee_national_id)
        assert employee is not None, "Employee existence should be validated in validate_generic_permit"

        from models.experience_years_policy_model import ExperienceYearsPolicy
        policies = ExperienceYearsPolicy.get_all_active_experience_years_policies()
        if not policies:
            logging.warning("No active experience years policy found.")
            return False, "No hay política de años de experiencia activa."

        # Dynamic target group validation (same as before)
        from models.target_group_model import TargetGroup

        # Calculate years of experience
        today = date.today()
        years_experience = today.year - employee.hire_date.year
        if (today.month, today.day) < (employee.hire_date.month, employee.hire_date.day):
            years_experience -= 1

        # Find the matching policy for the employee's years of experience
        matching_policy = None
        for policy in policies:
            if policy.years_to is None:
                if years_experience >= policy.years_from:
                    matching_policy = policy
                    break
            elif policy.years_from <= years_experience <= policy.years_to:
                matching_policy = policy
                break
        if not matching_policy:
            logging.info(f"No experience years policy matches {years_experience} years for employee {employee_national_id}")
            return False, "No existe una política para tus años de experiencia."

        # Target group validation
        target_group = TargetGroup.get_target_group_by_id(matching_policy.target_group_id)
        target_group_name = target_group.target_group_name.lower() if target_group else ""
        if target_group_name != "todos":
            employee_payroll_type = getattr(employee, "payroll_type", "").lower()
            if not (employee_payroll_type == target_group_name):
                logging.info(
                    f"Employee {employee_national_id} does not belong to target group '{target_group_name}'. Payroll type: {employee_payroll_type}"
                )
                return False, f"Solo personal {target_group_name} puede solicitar este permiso."

        # Check if the employee meets the vacation condition from policy
        available_vacation_days: int = PermitsLogic.get_available_vacation_days(employee_national_id)
        if not meets_condition(matching_policy.vacation_condition, available_vacation_days):
            logging.info(
                f"Employee {employee_national_id} does not meet vacation condition '{matching_policy.vacation_condition}' (has {available_vacation_days} days)."
            )
            return False, f"No cumples la condición de vacaciones ({matching_policy.vacation_condition.replace('_', ' ')}) para solicitar este permiso."

        # Count how many experience permits the employee has already used this year
        permits = PermitRequest.get_permits_by_employee_national_id(employee_national_id)
        used_days = 0
        for permit in permits:
            permit_type = PermitType.get_permit_type_by_id(permit.permit_type_id)
            if (
                permit_type and
                permit_type.permit_type_name.lower() == "beneficio años de experiencia" and
                permit.absence_date.year == selected_date.year and
                permit.status.lower() in ("aprobado", "pendiente")
            ):
                used_days += 1

        # Check if the employee has remaining days for this benefit
        allowed_days = matching_policy.allowed_days  # e.g., 2, 3, or 4
        if used_days >= allowed_days:
            logging.info(f"Employee {employee_national_id} has already used all allowed experience benefit days for {selected_date.year}.")
            return False, "Ya has utilizado todos los días permitidos por años de experiencia este año."

        logging.info(f"Experience years benefit validated for employee {employee_national_id} on {selected_date}.")
        return True, "Permiso de años de experiencia válido."
    
    @staticmethod
    def validate_generic_permit(
        employee_national_id: str,
        absence_date: date
    ) -> Tuple[bool, str]:
        """
        Generic validation for all permits:
        - Employee exists
        - Date is not in the past
        - Date is a business day
        - No overlapping approved or pending permit for that date
        """
        employee = Employee.get_employee_by_national_id(employee_national_id)
        if not employee:
            return False, "Empleado no encontrado."
        if absence_date < date.today():
            return False, "No se puede solicitar un permiso para una fecha pasada."

        # Check if the date is a business day
        is_business, business_msg = PermitsLogic.is_permit_date_business_day(absence_date)
        if not is_business:
            return False, business_msg

        # Check for overlapping permit
        overlap, overlap_msg = PermitsLogic.has_overlapping_permit(employee_national_id, absence_date)
        if overlap:
            return False, overlap_msg

        return True, ""

    @staticmethod
    def create_permit_request(
        request_date: date,
        absence_date: date,
        check_in_time: time,
        check_out_time: time,
        status: str,
        week_number: int,
        employee_national_id: str,
        permit_type_id: int,
        approver_national_id: str
    ) -> Tuple[bool, str]:
        """
        Validates and creates a permit request, saving it to the database.
        Returns (True, "") if created successfully, (False, reason) otherwise.
        """
        # Get permit type name
        permit_type = PermitType.get_permit_type_by_id(permit_type_id)
        if not permit_type:
            return False, "Tipo de permiso no válido."

        permit_type_name = permit_type.permit_type_name.lower()

        # Always check generic rules first
        valid, msg = PermitsLogic.validate_generic_permit(employee_national_id, absence_date)
        if not valid:
            return False, msg

        # Special validation for "Beneficio años de experiencia"
        if permit_type_name == "beneficio años de experiencia":
            valid, msg = PermitsLogic.validate_experience_years_benefit(employee_national_id, absence_date)
            if not valid:
                return False, msg

        # # Special validation for "Beneficio cumpleaños"
        # elif permit_type_name == "beneficio cumpleaños":
        #     valid, msg = PermitsLogic.validate_birthday_benefit(employee_national_id, absence_date)
        #     if not valid:
        #         return False, msg

        # Save permit
        result = PermitRequest.save_permit(
            request_date=request_date,
            absence_date=absence_date,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            status=status,
            week_number=week_number,
            employee_national_id=employee_national_id,
            permit_type_id=permit_type_id,
            approver_national_id=approver_national_id
        )
        if result:
            return True, ""
        else:
            return False, "Error al guardar la solicitud de permiso en la base de datos."

def meets_condition(condicion: str, vacation_days: int) -> bool:
    import logging
    if '_' not in condicion:
        logging.error(f"Malformed condition: {condicion}")
        raise ValueError(f"Malformed condition: {condicion}")
    operador, valor_str = condicion.split('_')
    valor = int(valor_str)

    result = None
    if operador == 'EQ':
        result = vacation_days == valor
    elif operador == 'LT':
        result = vacation_days < valor
    elif operador == 'LE':
        result = vacation_days <= valor
    elif operador == 'GT':
        result = vacation_days > valor
    elif operador == 'GE':
        result = vacation_days >= valor
    elif operador == 'NE':
        result = vacation_days != valor
    else:
        logging.error(f"Unknown operator: {operador}")
        raise ValueError(f"Unknown operator: {operador}")

    logging.info(f"Evaluating condition '{condicion}': days={vacation_days} => {result}")
    return result