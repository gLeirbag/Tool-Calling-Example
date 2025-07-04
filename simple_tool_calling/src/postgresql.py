import psycopg2
import sys

connection = None

def connect_to_postgresql():
    global connection
    try:
        connection = psycopg2.connect(
            "dbname=experimentos user=postgres password=admin"
        )
    except psycopg2.Error as e:
        print("🚫 Could not connect to PostgreSQL")
        print(e)
        print("🚫 The application's purpose will not be able to be demonstrated")
        sys.exit(1)

def get_comida_favorita(nome: str):
    cursor = connection.cursor()
    cursor.execute(f"SELECT comida FROM comida_favorita WHERE nome_pessoa='{nome}'")

    records = cursor.fetchall()
    record = records[0][0]
    return record
