import mysql.connector

def conexion():
    config = {
        "host": '127.0.0.1',
        "port": "3306",
        "user": "root",
        "password": "",
        "database": "datosalumnos"
    }
    return mysql.connector.connect(**config)