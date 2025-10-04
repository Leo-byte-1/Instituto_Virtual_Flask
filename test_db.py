from dotenv import load_dotenv
import os
import traceback

load_dotenv()
print('Loaded .env')
print('DATABASE_URL=', os.getenv('DATABASE_URL'))
print('DB_HOST=', os.getenv('DB_HOST'))
print('DB_PORT=', os.getenv('DB_PORT'))
print('DB_USER=', os.getenv('DB_USER'))
print('DB_NAME=', os.getenv('DB_NAME'))

import database
try:
    conn = database.conexion()
    print('CONNECTED:', conn)
    conn.close()
    print('CLOSED')
except Exception as e:
    print('ERROR:', e)
    traceback.print_exc()
