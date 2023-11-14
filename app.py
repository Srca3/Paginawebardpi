from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime
import serial
import json
app = Flask(__name__)

# Configuración del puerto serial
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Conexión a la base de datos SQLite (crea una base de datos si no existe)
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Crea la tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        lluvia REAL,
        radiacion_uv REAL
    )
''')
conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    # Leer datos del puerto serial
    data = ser.readline().decode('utf-8').strip()
    data_dict = json.loads(data)

    # Almacena los datos en la base de datos SQLite
    cursor.execute('''
        INSERT INTO weather_data (lluvia, radiacion_uv)
        VALUES (?, ?)
    ''', (data_dict['lluvia'], data_dict['radiacion_uv']))
    conn.commit()

    return jsonify(data_dict)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
