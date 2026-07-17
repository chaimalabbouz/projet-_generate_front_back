import os
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "llm_user"),
        password=os.getenv("MYSQL_PASSWORD", "1234"),
        database=os.getenv("MYSQL_DATABASE", "llm_config"),
    )