from flask import Flask, render_template, jsonify
import serial
import json
import sqlite3
from datetime import datetime
import random
from threading import Thread
import time

app = Flask(__name__)

try:
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
except serial.serialutil.SerialException:
    ser = None

# Elimina la conexión global a la base de datos y el cursor

# Crea la tabla si no existe en cada solicitud
def create_table():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            lluvia REAL,
            radiacion_uv REAL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/real-time')
def real_time():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Selecciona los últimos N datos de la tabla (ajusta según sea necesario)
    cursor.execute('SELECT * FROM weather_data ORDER BY timestamp DESC LIMIT 10')
    historical_data = cursor.fetchall()

    conn.close()

    return render_template('real-time.html', historical_data=historical_data)



def update_data_periodically():
    while True:
        create_table()

        if ser:
            data = ser.readline().decode('utf-8').strip()
            data_dict = json.loads(data)
        else:
            data_dict = {
                'lluvia': random.uniform(0, 10),
                'radiacion_uv': random.uniform(0, 10)
            }

        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO weather_data (lluvia, radiacion_uv)
            VALUES (?, ?)
        ''', (data_dict['lluvia'], data_dict['radiacion_uv']))
        conn.commit()

        conn.close()

        time.sleep(5)  # Actualiza cada 5 segundos (ajusta según sea necesario)

# Inicia la tarea en segundo plano
update_thread = Thread(target=update_data_periodically)
update_thread.start()


@app.route('/data')
def data():
    create_table()  # Crea la tabla antes de cada solicitud
    if ser:
        data = ser.readline().decode('utf-8').strip()
        data_dict = json.loads(data)
    else:
        data_dict = {
            'lluvia': random.uniform(0, 10),
            'radiacion_uv': random.uniform(0, 10)
        }

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO weather_data (lluvia, radiacion_uv)
        VALUES (?, ?)
    ''', (data_dict['lluvia'], data_dict['radiacion_uv']))
    conn.commit()

    conn.close()

    return jsonify(data_dict)

@app.route('/historial')
def historial():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Selecciona todos los datos de la tabla
    cursor.execute('SELECT * FROM weather_data')
    data = cursor.fetchall()

    conn.close()

    return render_template('historial.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
