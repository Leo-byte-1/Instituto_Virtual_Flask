from flask import Flask, render_template, request, redirect, url_for
import os 
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder = template_dir)

@app.route("/")
def inicio():

    return render_template("index.html")

@app.route("/lista-alumnos")
def lista_alumnos():
    conn = db.conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alumnos")
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    conn.close()

    return render_template("lista_alumnos.html", data = insertObject)

@app.route("/user", methods=["POST"])
def addUser():
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    edad = request.form["edad"]

    if nombre and apellido and edad:
        conn = db.conexion()
        cursor = conn.cursor()
        sql = "INSERT INTO alumnos (nombre, apellido, edad) VALUES (%s, %s, %s)"
        datos = (nombre, apellido, edad)
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
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    edad = request.form['edad']

    if nombre and apellido and edad:
        conn = db.conexion()
        cursor = conn.cursor()
        sql = "UPDATE alumnos SET nombre = %s, apellido = %s, edad = %s WHERE id = %s"
        data = (nombre, apellido, edad, id)
        cursor.execute(sql, data)
        db.conexion.commit()
        
        return redirect(url_for('lista_alumnos'))

@app.route("/registro")
def registrar():

    return render_template("registro.html")

@app.route("/calificaciones")
def calificaciones():

    return render_template("calificaciones.html")

@app.route("/fechas")
def fechas():

    return render_template("fechas.html")

if __name__ == "__main__":
    app.run(debug=True, port=4000)