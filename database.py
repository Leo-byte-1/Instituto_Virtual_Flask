import os
import psycopg2


def conexion():
    # Permitir una URL completa de conexión (ej. proporcionada por un PaaS)
    # Si existe DATABASE_URL, usarla como DSN.
    database_url = os.getenv('DATABASE_URL') or os.getenv('DB_URL')

    # Si DB_HOST contiene una URL completa accidentalmente, también la aceptamos
    db_host = os.getenv('DB_HOST')

    if database_url:
        try:
            # psycopg2 acepta la URI/DSN directamente
            return psycopg2.connect(database_url)
        except Exception:
            # Re-raise con más contexto
            raise

    if db_host and (db_host.startswith('postgres://') or db_host.startswith('postgresql://')):
        try:
            return psycopg2.connect(db_host)
        except Exception:
            raise

    # Configurar desde variables separadas (host/port/user/password/dbname)
    config = {
        'host': db_host or os.getenv('DB_HOST', '127.0.0.1'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'dbname': os.getenv('DB_NAME', 'datosalumnos'),
    }

    # psycopg2 lanzará una excepción si la conexión falla; la app
    # puede manejarla más arriba si se desea.
    return psycopg2.connect(**config)