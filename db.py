import psycopg2

params = {
    "host": "192.168.203.30",
    "port": 5432,
    "user": "emma",
    "password": "1dls1ekfr",
    "dbname": "emma"
}

def insert(table_name, list_of_dict):
    with psycopg2.connect(**params) as conn:
        columns = list_of_dict[0].keys()
        placeholders = [f"%({c})s" for c in columns]
        query = f"insert into {table_name} ({','.join(columns)}) values ({','.join(placeholders)})"
        with conn.cursor() as cursor:
            for d in list_of_dict:
                cursor.execute(query, d)
        conn.commit()

