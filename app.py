from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from sqlite3 import Error
import os

# Configuración inicial
app = Flask(__name__)
app.secret_key = "clave_secreta_para_mensajes"

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DATABASE_FILE = os.path.join(BASE_DIR, "delitos_2023.db")

def sql_connection():
    try:
        db = sqlite3.connect(DATABASE_FILE)
        return db
    except Error as e:
        print(e)
        return None

@app.route('/')
@app.route('/<int:page>')
def index(page=1):
    db = sql_connection()
    cursor = db.cursor()
    limit = 30
    offset = (page - 1) * limit
    cursor.execute(f"""SELECT Delitos.delito_id, Dias.nombre_dia, fecha_delito_dia_numero, Meses.nombre_mes, \
                     franja_horaria, Barrios.nombre_barrio, uso_arma, uso_moto, Tipo_Delitos.tipo_delito, info_adicional\
                     FROM Delitos \
                     INNER JOIN Dias ON Delitos.fecha_delito_dia_id = Dias.fecha_delito_dia_id \
                     INNER JOIN Meses ON Delitos.fecha_delito_mes_id = Meses.fecha_delito_mes_id \
                     INNER JOIN Barrios ON Delitos.barrio_id = Barrios.barrio_id \
                     INNER JOIN Tipo_Delitos ON Delitos.tipo_delito_id = Tipo_Delitos.tipo_delito_id \
                     LIMIT {limit} OFFSET {offset}""")
    data = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM Delitos")
    total_rows = cursor.fetchone()[0]
    total_pages = (total_rows // limit) + (1 if total_rows % limit > 0 else 0)

    cursor.close()
    db.close()
    return render_template('index.html', delitos=data, page=page, total_pages=total_pages)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            db = sql_connection()
            data = (
                request.form['fecha_delito_dia_id'],
                request.form['fecha_delito_dia_numero'],
                request.form['fecha_delito_mes_id'],
                request.form['fecha_delito_ano'],
                request.form['franja_horaria'],
                request.form['barrio_id'],
                request.form['uso_arma'],
                request.form['uso_moto'],
                request.form['tipo_delito_id'],
                request.form['info_adicional']
            )
            cursor = db.cursor()
            cursor.execute("""INSERT INTO Delitos 
                              (fecha_delito_dia_id, fecha_delito_dia_numero, fecha_delito_mes_id, fecha_delito_ano, 
                               franja_horaria, barrio_id, uso_arma, uso_moto, tipo_delito_id, info_adicional) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", data)
            db.commit()
            cursor.close()
            db.close()
            flash('Delito agregado exitosamente')
            return redirect(url_for('index'))
        except Error as e:
            flash(f'Error: {e}')
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = sql_connection()
    if request.method == 'POST':
        try:
            data = (
                request.form['fecha_delito_dia_id'],
                request.form['fecha_delito_dia_numero'],
                request.form['fecha_delito_mes_id'],
                request.form['fecha_delito_ano'],
                request.form['franja_horaria'],
                request.form['barrio_id'],
                request.form['uso_arma'],
                request.form['uso_moto'],
                request.form['tipo_delito_id'],
                request.form['info_adicional'],
                id
            )
            cursor = db.cursor()
            cursor.execute("""UPDATE Delitos 
                              SET fecha_delito_dia_id = ?, fecha_delito_dia_numero = ?, fecha_delito_mes_id = ?, 
                                  fecha_delito_ano = ?, franja_horaria = ?, barrio_id = ?, uso_arma = ?, 
                                  uso_moto = ?, tipo_delito_id = ?, info_adicional = ? 
                              WHERE delito_id = ?""", data)
            db.commit()
            cursor.close()
            db.close()
            flash('Delito actualizado exitosamente')
            return redirect(url_for('index'))
        except Error as e:
            flash(f'Error: {e}')
    else:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Delitos WHERE delito_id = ?", (id,))
        delito = cursor.fetchone()
        cursor.close()
        db.close()
        return render_template('edit.html', delito=delito)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    try:
        db = sql_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM Delitos WHERE delito_id = ?", (id,))
        db.commit()
        cursor.close()
        db.close()
        flash('Delito eliminado exitosamente')
    except Error as e:
        flash(f'Error: {e}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
