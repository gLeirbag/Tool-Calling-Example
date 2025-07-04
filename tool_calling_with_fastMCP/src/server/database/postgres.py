import psycopg2

connection = None

def connect_to_postgresql():
    global connection
    connection = psycopg2.connect(
        "dbname=experimentos user=postgres password=admin"
    )


def get_comida_favorita(nome: str):
    cursor = connection.cursor()
    cursor.execute(f"SELECT comida FROM comida_favorita WHERE nome_pessoa='{nome}'")

    records = cursor.fetchall()
    record = records[0][0]
    return record
