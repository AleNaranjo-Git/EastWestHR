from typing import Literal
import bcrypt
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
        return "connection_error"

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT contrasena_hasheada 
            FROM usuario 
            WHERE correo_login = ?
        """, (email,))
        
        result = cursor.fetchone()
        if not result:
            return "invalid_user"

        hashed_pw = result[0]

        if not bcrypt.checkpw(password.encode('utf-8'), hashed_pw.encode('utf-8')):
            return "invalid_password"

        return "success"

    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return "connection_error"
    finally:
        db.close()