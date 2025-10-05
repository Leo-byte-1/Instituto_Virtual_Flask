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
        """Intentar una conexión real a la base de datos y devolver el resultado."""
        try:
            conn = db.conexion()
            conn.close()
            return jsonify({'db': 'ok'})
        except Exception as e:
            return render_template('error.html', error=str(e)), 500

    @app.route("/")
    def inicio():
        return render_template("index.html")

    @app.route('/index.html')
    def index_html():
        return redirect(url_for('inicio'))

    @app.route("/lista-alumnos")
    def lista_alumnos():
        try:
            conn = db.conexion()
        except Exception as e:
            return render_template('error.html', error=str(e))
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute("SELECT id, nombre, apellido, edad, dni FROM alumnos ORDER BY apellido, nombre")
            myresult = cursor.fetchall()
            insertObject = [dict(r) for r in myresult]
        except Exception as e:
            cursor.close()
            conn.close()
            return render_template('error.html', error=str(e))

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

        nombre = request.form["nombre"].strip()
        apellido = request.form["apellido"].strip()
        edad = request.form["edad"]
        dni = request.form["dni"]

        if nombre and apellido and edad and dni:
            sql = "INSERT INTO alumnos (nombre, apellido, edad, dni) VALUES (%s, %s, %s, %s)"
            datos = (nombre, apellido, edad, dni)
            cursor.execute(sql, datos)
            conn.commit()
            cursor.close()
            conn.close()
            # Redirigir con parámetro de éxito
            return redirect(url_for('lista_alumnos', success='added'))
        
        cursor.close()
        conn.close()
        return redirect(url_for('registrar'))

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

        # Redirigir con parámetro de éxito
        return redirect(url_for('lista_alumnos', success='deleted'))

    @app.route("/edit/<string:id>", methods=['POST'])
    def edit(id):
        try:
            conn = db.conexion()
        except Exception as e:
            return render_template('error.html', error=str(e))
        cursor = conn.cursor()
        nombre = request.form['nombre'].strip()
        apellido = request.form['apellido'].strip()
        edad = request.form['edad']
        dni = request.form["dni"]

        if nombre and apellido and edad and dni:
            sql = "UPDATE alumnos SET nombre = %s, apellido = %s, edad = %s, dni = %s WHERE id = %s"
            data = (nombre, apellido, edad, dni, id)
            cursor.execute(sql, data)
            conn.commit()
        
        cursor.close()
        conn.close()

        # Redirigir con parámetro de éxito
        return redirect(url_for('lista_alumnos', success='updated'))

    @app.route("/buscar", methods=['POST'])
    def buscar():
        buscar = request.form["buscar"].strip()
        try:
            conn = db.conexion()
        except Exception as e:
            return render_template('error.html', error=str(e))
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Búsqueda más flexible usando ILIKE para case-insensitive
        sql = """
            SELECT id, nombre, apellido, edad, dni 
            FROM alumnos 
            WHERE nombre ILIKE %s 
               OR apellido ILIKE %s 
               OR CAST(dni AS TEXT) LIKE %s
            ORDER BY apellido, nombre
        """
        search_pattern = f"%{buscar}%"
        params = (search_pattern, search_pattern, search_pattern)
        cursor.execute(sql, params)
        myresult = cursor.fetchall()
        insertObject = [dict(r) for r in myresult]
        cursor.close()
        conn.close()

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
        try:
            cursor.execute("""
                SELECT a.nombre, m.materia, n.notas 
                FROM notas n 
                JOIN alumnos a ON n.id_alumno = a.id 
                JOIN materias m ON m.id_materia = n.id_materia 
                ORDER BY a.apellido, a.nombre, m.materia
            """)
            myresult = cursor.fetchall()
            insertObjectC = [dict(r) for r in myresult]
        except Exception as e:
            cursor.close()
            conn.close()
            return render_template('error.html', error=str(e))

        cursor.close()
        conn.close()

        return render_template("calificaciones.html", notas=insertObjectC)

    @app.route('/db-tables')
    def db_tables():
        """Ruta diagnóstica que lista tablas no-sistema visibles por el usuario de la BD."""
        try:
            conn = db.conexion()
        except Exception as e:
            return render_template('error.html', error=str(e))
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute("""
                SELECT schemaname, tablename
                FROM pg_catalog.pg_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY schemaname, tablename
            """)
            tables = cursor.fetchall()
        except Exception as e:
            cursor.close()
            conn.close()
            return render_template('error.html', error=str(e))

        cursor.close()
        conn.close()
        from flask import jsonify
        return jsonify(tables)

    @app.route('/calificaciones-debug')
    def calificaciones_debug():
        """Ruta de diagnóstico: devuelve conteos y algunas filas de ejemplo de las tablas usadas por /calificaciones.

        Útil para verificar rápidamente si la BD tiene datos o si la consulta no encuentra filas.
        """
        try:
            conn = db.conexion()
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute("SELECT count(*) AS cnt FROM alumnos")
            alumnos_cnt = cursor.fetchone()['cnt']
        except Exception:
            alumnos_cnt = None
        try:
            cursor.execute("SELECT count(*) AS cnt FROM materias")
            materias_cnt = cursor.fetchone()['cnt']
        except Exception:
            materias_cnt = None
        try:
            cursor.execute("SELECT count(*) AS cnt FROM notas")
            notas_cnt = cursor.fetchone()['cnt']
        except Exception:
            notas_cnt = None

        try:
            cursor.execute("""
                SELECT a.nombre, m.materia, n.notas
                FROM notas n
                JOIN alumnos a ON n.id_alumno = a.id
                JOIN materias m ON m.id_materia = n.id_materia
                ORDER BY a.apellido, a.nombre, m.materia
                LIMIT 10
            """)
            sample = [dict(r) for r in cursor.fetchall()]
        except Exception:
            sample = []

        cursor.close()
        conn.close()

        return jsonify({
            'alumnos_count': alumnos_cnt,
            'materias_count': materias_cnt,
            'notas_count': notas_cnt,
            'sample': sample
        })

    @app.errorhandler(404)
    def page_not_found(error):
        mensaje = f"Not Found: {request.path}"
        return render_template('error.html', error=mensaje), 404
    
    return app


# Registrar rutas en el momento de la importación
app = crear_app()