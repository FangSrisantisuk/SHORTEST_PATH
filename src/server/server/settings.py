import os

from sqlalchemy import URL

# Load environment variables
DATABASE = "mssql"
DIALECT = "pyodbc"
DB_USR = os.getenv("DB_USR", "db_app_dev")
DB_PASSWD = os.getenv("DB_PASSWD", "Password@123456")
DB_ADDR = os.getenv("DB_ADDR", "172.18.0.1")
DB_PORT = os.getenv("DB_PORT", 1433)
DB_NAME = os.getenv("DB_NAME", "TestDB")
connection_url = URL.create(
    f"{DATABASE}+{DIALECT}",
    username=DB_USR,
    password=DB_PASSWD,
    host=DB_ADDR,
    port=DB_PORT,
    database=DB_NAME,
    query={
        "driver": "ODBC Driver 17 for SQL Server",
        "TrustServerCertificate": "yes",
    }
)
