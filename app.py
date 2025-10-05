from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
import database as db

# Cargar variables de entorno
load_dotenv()

def crear_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')

    # Logger simple para todas las peticiones
    @app.before_request
    def _log_request():
        print(f"Request: {request.method} {request.path}")

    # --------------------- RUTAS ---------------------

    @app.route('/health')
    def health():
        routes = [str(r) for r in app.url_map.iter_rules()]
        return jsonify({'status': 'ok', 'routes': routes})

    @app.route('/db-check')
    def db_check():
        """Probar conexión con la base de datos."""
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
        return redirect(url_for('lista_alumnos', success='updated'))

    @app.route("/buscar", methods=['POST'])
    def buscar():
        buscar = request.form["buscar"].strip()
        try:
            conn = db.conexion()
        except Exception as e:
            return render_template('error.html', error=str(e))
        cursor = conn.cursor(cursor_factory=RealDictCursor)

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
        conn = None
        cursor = None
    
        try:
            conn = db.conexion()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        
            # Query mejorada con más información de depuración
            cursor.execute("""
                SELECT 
                    a.nombre, 
                    a.apellido,
                    m.materia, 
                    n.notas 
                FROM notas n 
                JOIN alumnos a ON n.id_alumno = a.id 
                JOIN materias m ON m.id_materia = n.id_materia 
                ORDER BY a.apellido, a.nombre, m.materia
            """)
            myresult = cursor.fetchall()
            insertObjectC = [dict(r) for r in myresult]
            
            # Debug: imprimir en consola
            print(f"[DEBUG] Total de calificaciones encontradas: {len(insertObjectC)}")
            if len(insertObjectC) > 0:
                print(f"[DEBUG] Primera calificación: {insertObjectC[0]}")
            else:
                print("[DEBUG] No se encontraron calificaciones en la base de datos")
        
        except Exception as e:
            print(f"[ERROR] Error en query de calificaciones: {str(e)}")
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            return render_template('error.html', error=str(e))
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
        # Asegurarnos de que siempre se pase la variable 'notas'
        return render_template("calificaciones.html", notas=insertObjectC if insertObjectC else [])

    @app.route('/db-tables')
    def db_tables():
        """Lista tablas visibles (no del sistema)."""
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
        return jsonify(tables)

    @app.route('/calificaciones-debug')
    def calificaciones_debug():
        """Ruta de diagnóstico de conteos y muestras."""
        try:
            conn = db.conexion()
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        def safe_count(query):
            try:
                cursor.execute(query)
                return cursor.fetchone()['cnt']
            except Exception:
                return None

        alumnos_cnt = safe_count("SELECT count(*) AS cnt FROM alumnos")
        materias_cnt = safe_count("SELECT count(*) AS cnt FROM materias")
        notas_cnt = safe_count("SELECT count(*) AS cnt FROM notas")

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

    # --------------------- ERRORES ---------------------

    @app.errorhandler(404)
    def page_not_found(error):
        mensaje = f"Not Found: {request.path}"
        return render_template('error.html', error=mensaje), 404

    return app


# Crear la aplicación
app = crear_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
