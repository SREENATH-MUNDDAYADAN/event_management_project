from dotenv import load_dotenv
load_dotenv()
import os
import mysql.connector
from mysql.connector import Error

def get_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'event_management'),
        autocommit=False
    )

def query(sql, params=(), fetch=False):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        result = cur.fetchall() if fetch else cur.lastrowid
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
