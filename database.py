import os
import psycopg2

def conexion():
    # Conexión desde variables separadas
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT') or 5432
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    dbname = os.getenv('DB_NAME')

    return psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname, sslmode='require', connect_timeout=5)