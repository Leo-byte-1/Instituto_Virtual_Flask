import os
import psycopg2


def conexion():
    """Crear y devolver una conexión a PostgreSQL.

    Lee la configuración desde variables de entorno con valores por
    defecto para desarrollo. Ejemplos de variables:
      - DB_HOST (por defecto 127.0.0.1)
      - DB_PORT (por defecto 5432)
      - DB_USER
      - DB_PASSWORD
      - DB_NAME (por defecto datosalumnos)

    Retorna: objeto psycopg2.connection
    """
    config = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'dbname': os.getenv('DB_NAME', 'datosalumnos'),
    }

    # psycopg2 lanzará una excepción si la conexión falla; la app
    # puede manejarla más arriba si se desea.
    return psycopg2.connect(**config)