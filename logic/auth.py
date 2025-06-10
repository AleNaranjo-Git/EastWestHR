from typing import Literal
import bcrypt
import logging
from db.connection import DatabaseConnection

AuthResult = Literal["success", "connection_error", "invalid_user", "invalid_password"]

def authenticate(email: str, password: str) -> AuthResult:
    """
    Authenticates user credentials against database.
    
    Args:
        email: User's login email
        password: User's password (plain text)
        
    Returns:
        AuthResult: Authentication result status
    """
    db = DatabaseConnection()
    conn = db.connect()
    
    if not conn:
        logging.error("Database connection error during authentication.")
        return "connection_error"

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT hashed_password 
            FROM user_account 
            WHERE login_email = ?
        """, (email,))
        
        result = cursor.fetchone()
        if not result:
            logging.warning(f"Authentication failed: invalid user '{email}'.")
            return "invalid_user"

        hashed_pw = result[0]

        if not bcrypt.checkpw(password.encode('utf-8'), hashed_pw.encode('utf-8')):
            logging.warning(f"Authentication failed: invalid password for user '{email}'.")
            return "invalid_password"

        logging.info(f"User '{email}' authenticated successfully.")
        return "success"

    except Exception as e:
        logging.error(f"Authentication error for user '{email}': {str(e)}")
        return "connection_error"
    finally:
        db.close()