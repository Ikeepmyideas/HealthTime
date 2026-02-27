import psycopg2
from config import settings

def get_connection():
    try:
        conn = psycopg2.connect(
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT
        )
        print("Connection to DB successful")
        return conn
    except Exception as e:
        print("Connection to DB failed:", e)
        return None
