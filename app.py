from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
import database as db
from flask import jsonify

# Cargar variables de entorno desde el archivo .env si existe
load_dotenv()

app = Flask(__name__)
# Configurar SECRET_KEY desde variables de entorno (evita hardcodear credenciales)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')

def crear_app():
    # Registrar un logger sencillo para todas las peticiones
    @app.before_request
    def _log_request():
        print(f"Request: {request.method} {request.path}")

    @app.route('/health')
    def health():
        # Devuelve OK y lista de rutas registradas para diagnóstico
        routes = [str(r) for r in app.url_map.iter_rules()]
        return jsonify({'status': 'ok', 'routes': routes})

    @app.route('/db-check')
    def db_check():
        """Intentar una conexión real a la base de datos y devolver el resultado.

        Útil para confirmar que el host/puerto/credenciales son accesibles desde
        la máquina donde corre la app.
        """
        try:
            conn = db.conexion()
            conn.close()
            return jsonify({'db': 'ok'})
        except Exception as e:
            # Devolver el error para diagnóstico; en producción podrías ocultar detalles
            return render_template('error.html', error=str(e)), 500

    @app.route("/")
    def inicio():

        return render_template("index.html")

    @app.route("/lista-alumnos")
    def lista_alumnos():
        try:
            conn = db.conexion()
        except Exception as e:
            return render_template('error.html', error=str(e))
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
        try:
            conn = db.conexion()
        except Exception as e:
            return render_template('error.html', error=str(e))
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
        try:
            conn = db.conexion()
        except Exception as e:
            return render_template('error.html', error=str(e))
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
        try:
            conn = db.conexion()
        except Exception as e:
            return render_template('error.html', error=str(e))
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
        try:
            conn = db.conexion()
        except Exception as e:
            return render_template('error.html', error=str(e))
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
        try:
            conn = db.conexion()
        except Exception as e:
            return render_template('error.html', error=str(e))
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT a.nombre, m.materia, n.notas FROM notas n JOIN alumnos a ON n.id_alumno = a.id_alumno JOIN materias m ON m.id_materia = n.id_materia ORDER BY a.nombre")
        myresult = cursor.fetchall()
        # ya son dicts
        insertObjectC = [dict(r) for r in myresult]
        cursor.close()
        conn.close()

        return render_template("calificaciones.html", notas=insertObjectC)
    return app


# Registrar rutas en el momento de la importación para que
# comandos como `flask run` funcionen correctamente.
app = crear_app()

if __name__ == "__main__":
    app.run(debug=True, port=4000)