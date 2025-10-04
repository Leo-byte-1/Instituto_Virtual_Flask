from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
import database as db

# Cargar variables de entorno desde el archivo .env si existe
load_dotenv()

app = Flask(__name__)
# Configurar SECRET_KEY desde variables de entorno (evita hardcodear credenciales)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')

def crear_app():
    @app.route("/")
    def inicio():

        return render_template("index.html")

    @app.route("/lista-alumnos")
    def lista_alumnos():
        conn = db.conexion()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, nombre, apellido, edad, dni FROM alumnos")
        myresult = cursor.fetchall()
        # ya son filas tipo dict; convertir explícitamente a dicts simples
        insertObject = [dict(r) for r in myresult]
        cursor.close()
        conn.close()

        return render_template("lista_alumnos.html", data=insertObject)

    @app.route("/user", methods=["POST"])
    def addUser():
        conn = db.conexion()
        cursor = conn.cursor()

        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        edad = request.form["edad"]
        dni = request.form["dni"]

        if nombre and apellido and edad and dni:
            sql = "INSERT INTO alumnos (nombre, apellido, edad, dni) VALUES (%s, %s, %s, %s)"
            datos = (nombre, apellido, edad, dni)
            cursor.execute(sql, datos)
            conn.commit()
            cursor.close()
            conn.close()

        return redirect(url_for('lista_alumnos'))

    @app.route("/delete/<string:id>")
    def delete(id):
        conn = db.conexion()
        cursor = conn.cursor()
        sql = "DELETE FROM alumnos WHERE id=%s"
        data = (id,)
        cursor.execute(sql, data)
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('lista_alumnos'))

    @app.route("/edit/<string:id>", methods=['POST'])
    def edit(id):
        conn = db.conexion()
        cursor = conn.cursor()
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        edad = request.form['edad']
        dni = request.form["dni"]

        if nombre and apellido and edad:
            sql = "UPDATE alumnos SET nombre = %s, apellido = %s, edad = %s, dni = %s WHERE id = %s"
            data = (nombre, apellido, edad, dni, id)
        cursor.execute(sql, data)
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('lista_alumnos'))

    @app.route("/buscar", methods=['POST'])
    def buscar():
        buscar = request.form["buscar"]
        conn = db.conexion()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Seleccionar las mismas columnas que usa la plantilla
        sql = "SELECT id, nombre, apellido, edad, dni FROM alumnos WHERE nombre = %s"
        params = (buscar,)
        cursor.execute(sql, params)
        myresult = cursor.fetchall()
        insertObject = [dict(r) for r in myresult]
        cursor.close()
        conn.close()

        # Devolver como 'data' para que la plantilla principal la use de forma consistente
        return render_template("lista_alumnos.html", data=insertObject)

    @app.route("/registro")
    def registrar():

        return render_template("registro.html")

    @app.route("/calificaciones")
    def calificaciones():
        conn = db.conexion()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT a.nombre, m.materia, n.notas FROM notas n JOIN alumnos a ON n.id_alumno = a.id_alumno JOIN materias m ON m.id_materia = n.id_materia ORDER BY a.nombre")
        myresult = cursor.fetchall()
        # ya son dicts
        insertObjectC = [dict(r) for r in myresult]
        cursor.close()
        conn.close()

        return render_template("calificaciones.html", notas=insertObjectC)
    return app

if __name__ == "__main__":
    app = crear_app()
    app.run(debug=True, port=5000)