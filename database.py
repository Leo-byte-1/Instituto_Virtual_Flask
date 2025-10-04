import os
import psycopg2
from urllib.parse import urlparse


def conexion():
    """Crear y devolver una conexión a PostgreSQL.

    Reglas:
    - Si existe `DATABASE_URL` (o `DB_URL`) se intenta usarla primero.
      Intentamos conectarnos con `sslmode='require'` y con `connect_timeout=5`
      para evitar esperas largas cuando la base de datos remota no está accesible.
    - Si no hay `DATABASE_URL`, construimos la conexión desde
      `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` y `DB_NAME`.
    - Normalizamos nombres de BD con guiones reemplazándolos por guiones bajos
      y avisamos por stdout (solo ayuda en desarrollo).

    Lanza una excepción clara si faltan variables necesarias o falla la conexión.
    """

    database_url = os.getenv('DATABASE_URL') or os.getenv('DB_URL')

    # Si viene una URL completa, usarla (con SSL y timeout preferente)
    if database_url:
        # Intentar con sslmode y timeout corto para entornos remotos (Render, Heroku, etc.)
        try:
            return psycopg2.connect(database_url, sslmode='require', connect_timeout=5)
        except Exception as e_ssl:
            # Intentar sin forzar SSL si falla por algún motivo
            try:
                return psycopg2.connect(database_url, connect_timeout=5)
            except Exception as e_no_ssl:
                raise Exception(f"Fallo al conectar usando DATABASE_URL. Intentos: ssl error={e_ssl}; sin-ssl error={e_no_ssl}")

    # Si DB_HOST contiene accidentalmente una URL completa, también la aceptamos
    db_host = os.getenv('DB_HOST')
    if db_host and (db_host.startswith('postgres://') or db_host.startswith('postgresql://')):
        try:
            return psycopg2.connect(db_host, sslmode='require', connect_timeout=5)
        except Exception as e:
            raise Exception(f"Fallo al conectar usando DB_HOST como URL: {e}")

    # Conexión desde variables separadas
    host = db_host or os.getenv('DB_HOST')
    port = os.getenv('DB_PORT') or 5432
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    dbname = os.getenv('DB_NAME')

    # Normalizar dbname (algunos servicios usan guiones en lugar de guiones bajos)
    if dbname and '-' in dbname:
        suggested = dbname.replace('-', '_')
        print(f"Advertencia: DB_NAME contiene guiones. Usando '{suggested}' en su lugar. Actualiza .env si esto no es correcto.")
        dbname = suggested

    missing = [k for k, v in [('DB_HOST', host), ('DB_USER', user), ('DB_PASSWORD', password), ('DB_NAME', dbname)] if not v]
    if missing:
        raise Exception(f"Faltan variables de entorno para conectarse a la BD: {', '.join(missing)}")

    try:
        return psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname, sslmode='require', connect_timeout=5)
    except TypeError:
        # En caso de una versión antigua de psycopg2 que no acepte sslmode en kwargs,
        # intentamos sin sslmode (caerá con un error claro si realmente es necesario).
        return psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname, connect_timeout=5)