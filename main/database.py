import sqlite3
from config import DATABASE_NAME




def create_connection(conn):
    return sqlite3.connect(DATABASE_NAME)

def create_tables(conn):
    with create_connection(conn) as conn:
        cur = conn.cursor()
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                    tg INTEGER PRIMARY KEY,
                    fullname TEXT,
                    contacts TEXT,
                    education TEXT,
                    job_exp TEXT,
                    skills TEXT,
                    additional TEXT
                    )
                    """)
