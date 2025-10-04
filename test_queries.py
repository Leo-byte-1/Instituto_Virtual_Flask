from psycopg2.extras import RealDictCursor
import database
import traceback
from dotenv import load_dotenv
import os

print('Running test_queries.py')
load_dotenv()
print('DATABASE_URL=', os.getenv('DATABASE_URL'))
print('DB_HOST=', os.getenv('DB_HOST'))
print('DB_PORT=', os.getenv('DB_PORT'))
print('DB_USER=', os.getenv('DB_USER'))
print('DB_NAME=', os.getenv('DB_NAME'))

try:
    conn = database.conexion()
    print('Connected:', conn)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT id, nombre, apellido, edad, dni FROM alumnos LIMIT 10")
    alumnos = cur.fetchall()
    print('\nAlumnos rows count:', len(alumnos))
    for r in alumnos:
        print(r)

    cur.execute("SELECT a.nombre, m.materia, n.notas FROM notas n JOIN alumnos a ON n.id_alumno = a.id_alumno JOIN materias m ON m.id_materia = n.id_materia ORDER BY a.nombre LIMIT 10")
    notas = cur.fetchall()
    print('\nNotas rows count:', len(notas))
    for r in notas:
        print(r)

    cur.close()
    conn.close()
    print('\nDone')
except Exception as e:
    print('ERROR:', e)
    traceback.print_exc()
