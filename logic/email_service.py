import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from models.employee_model import Employee
from models.email_credentials_model import EmailCredentials
import logging

def send_email(
    subject: str,
    body: str,
    recipients: List[str],
    smtp_server: str = "smtp.office365.com",  # Cambiado a Microsoft 365
    smtp_port: int = 587,  # Puerto para Microsoft 365
) -> bool:
    """
    Sends an email using the provided SMTP server.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
        recipients (List[str]): A list of recipient email addresses.
        smtp_server (str): The SMTP server address (default: "smtp.office365.com").
        smtp_port (int): The SMTP server port (default: 587).

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    # Obtain the credentials from the database
    credentials = EmailCredentials.get_credentials()

    if not credentials:
        logging.error("Error: No se pudieron obtener las credenciales de correo.")
        return False

    sender_email = credentials["usuario"]
    sender_password = credentials["clave"]

    try:
        # Create the email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())

        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def fetch_recipients(national_id: str, supervisor_national_id: str, additional_emails: List[str]) -> List[str]:
    """
    Fetches the email recipients based on the employee's national ID, supervisor's national ID, 
    and a list of additional email addresses.

    Args:
        national_id (str): The national ID of the employee (can be None).
        supervisor_national_id (str): The national ID of the supervisor (can be None).
        additional_emails (List[str]): A list of additional email addresses.

    Returns:
        List[str]: A list of email addresses to send the email to.
    """
    recipients: List[str] = []

    # Fetch the employee's email if national_id is provided
    if national_id:
        employee_email = Employee.get_email_by_national_id(national_id)
        if employee_email:
            recipients.append(employee_email)
        else:
            logging.warning(f"No email found for national_id: {national_id}")
    else:
        logging.info("No national_id provided, skipping employee email.")

    # Fetch the supervisor's email if supervisor_national_id is provided
    if supervisor_national_id:
        supervisor_email = Employee.get_email_by_national_id(supervisor_national_id)
        if supervisor_email:
            recipients.append(supervisor_email)
        else:
            logging.warning(f"No email found for supervisor_national_id: {supervisor_national_id}")
    else:
        logging.info("No supervisor_national_id provided, skipping supervisor email.")

    # Add the additional emails
    recipients.extend(additional_emails)

    return recipients