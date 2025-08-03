import pyodbc
from dotenv import load_dotenv
import os
import logging

class DatabaseConnection:
    def __init__(self):
        load_dotenv()
        self.server = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.database = os.getenv("DB_NAME")
        self.username = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.conn = None

    def connect(self):
        if not self.conn:
            try:
                self.conn = pyodbc.connect(
                    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                    f"SERVER={self.server},{self.port};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};"
                    f"PWD={self.password};"
                    f"Encrypt=no;"
                )
            except Exception as e:
                logging.error(f"Database connection error: {e}")
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
