origin = "http://localhost:3000"
DATABASE_PASSWORD = "3166"
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432

import psycopg2


def helper_select_db(select_query, values):
    connection = psycopg2.connect(database="postgres", user="postgres", password="3166", host="localhost", port=5432)
    cursor = connection.cursor()
    cursor.execute(select_query, values)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return result



def helper_insert_db(insert_query, values):
    connection = psycopg2.connect(database="postgres", user="postgres", password="3166", host="localhost", port=5432)
    cursor = connection.cursor()
    cursor.execute(insert_query, values)
    cursor.close()
    connection.commit()
    connection.close()