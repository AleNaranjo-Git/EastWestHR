import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from dotenv import load_dotenv
import os
from models.employee_model import Employee

# Load environment variables from .env
load_dotenv()

def send_email(
    subject: str,
    body: str,
    recipients: List[str],
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587,
) -> bool:
    """
    Sends an email using the provided SMTP server.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
        recipients (List[str]): A list of recipient email addresses.
        smtp_server (str): The SMTP server address (default: "smtp.gmail.com").
        smtp_port (int): The SMTP server port (default: 587).

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("Error: Missing sender email or password in environment variables.")
        return False

    try:
        # Create the email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())

        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def fetch_recipients(national_id: str, supervisor_national_id: str, departments: List[str]) -> List[str]:
    """
    Fetches the email recipients based on the employee's national ID and departments.

    Args:
        national_id (str): The national ID of the employee.
        departments (List[str]): A list of department names.

    Returns:
        List[str]: A list of email addresses to send the email to.
    """
    recipients: List[str] = []

    # Fetch the employee's email
    employee_email = Employee.get_email_by_national_id(national_id)
    if employee_email:
        recipients.append(employee_email)
        
    # Fetch the supervisor's email
    supervisor_email = Employee.get_email_by_national_id(supervisor_national_id)
    if supervisor_email:
        recipients.append(supervisor_email)

    # Fetch department-specific emails
    department_emails = Employee.get_emails_by_departments(departments)
    recipients.extend(department_emails)

    return recipients