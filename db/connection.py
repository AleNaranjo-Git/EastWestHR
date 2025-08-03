import pyodbc
from dotenv import load_dotenv
import os
import logging
from typing import Dict, Optional

class DatabaseConnection:
    def __init__(self):
        load_dotenv()
        self.connections: Dict[str, pyodbc.Connection] = {}
        self.configs = self._load_configs()
    
    def _load_configs(self) -> Dict[str, Dict[str, str]]:
        
        configs = {}
        
        # Principal database
        configs["main"] = {
            "server": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "database": os.getenv("DB_NAME"),
            "username": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD")
        }
        
        # VistaEmpleados database
        configs["secondary"] = {
            "server": os.getenv("DB_VE_HOST"),
            "port": os.getenv("DB_VE_PORT"),
            "database": os.getenv("DB_VE_NAME"),
            "username": os.getenv("DB_VE_USER"),
            "password": os.getenv("DB_VE_PASSWORD")
        }
        
        # Email credentials
        configs["email"] = {
            "server": os.getenv("DB_EMAIL_HOST"),
            "port": os.getenv("DB_EMAIL_PORT"),
            "database": os.getenv("DB_EMAIL_NAME"),
            "username": os.getenv("DB_EMAIL_USER"),
            "password": os.getenv("DB_EMAIL_PASSWORD")
        }
        
        return configs # type: ignore
    
    def get_connection(self, db_name: str) -> Optional[pyodbc.Connection]:
        """Obtiene una conexión a la base de datos especificada"""
        if db_name in self.connections:
            return self.connections[db_name]

        if db_name not in self.configs:
            logging.error(f"Configuration not found for database: {db_name}")
            return None

        config = self.configs[db_name]

        if not all(config.values()):
            logging.error(f"Incomplete configuration for {db_name}")
            return None

        # Construct the server with or without port
        if config["port"]:  # If the port is defined
            server = f"{config['server']},{config['port']}"
        else:  # If there is no port, just use the server
            server = config["server"]

        try:
            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={config['database']};"
                f"UID={config['username']};"
                f"PWD={config['password']};"
                f"Encrypt=no;"
            )
            self.connections[db_name] = conn
            return conn
        except Exception as e:
            logging.error(f"Error connecting to {db_name}: {e}")
            return None
    
    def close_connection(self, db_name: str):
        if db_name in self.connections:
            self.connections[db_name].close()
            del self.connections[db_name]
    
    def close_all_connections(self):
        for db_name in list(self.connections.keys()):
            self.close_connection(db_name)
