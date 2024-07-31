import psycopg2
from psycopg2 import sql


DB_NAME = 'dwell_fi'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_HOST = '127.0.0.1'
DB_PORT = '5432'

def create_database():
    conn = None
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        conn.autocommit = True
        cur = conn.cursor()

        # Drop the database if it exists
        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(DB_NAME)))
        
        # Create a new database
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        
        print(f"Database '{DB_NAME}' created successfully.")

    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
    
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_database()
