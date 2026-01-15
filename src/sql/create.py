import os
from psycopg2 import connect, Error

from src.sql.schema import (SCHEMA_DATA, INDEX_DATA,
                            SCHEMA_QUEUE, INDEX_QUEUE,
                            SCHEMA_ENUMS)

def create_connection():
    #Create connection to postgresql db
    try:
        conn = connect(
            host = os.getenv("DB_HOST"),
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD")
        )
        return conn
    except Error as e:
        print("Error connecting to PostgreSQL:", e)
    return conn

def create_table(conn):
    cur = conn.cursor()

    cur.execute(SCHEMA_ENUMS)
    cur.execute(SCHEMA_DATA)
    cur.execute(SCHEMA_QUEUE)
    cur.execute(INDEX_DATA)
    cur.execute(INDEX_QUEUE)

    cur.close()