from flask import Flask, render_template, jsonify, request
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
    return render_template('real-time.html')




@app.route('/data')
def data():
    create_table()  # Crea la tabla antes de cada solicitud
    data = request.get_json()
    
    if data:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO weather_data (lluvia, radiacion_uv)
            VALUES (?, ?)
        ''', (data['lluvia'], data['radiacion_uv']))
        
        conn.commit()
        conn.close()

        return jsonify({"message": "Data received successfully"})
    else:
        return jsonify({"error": "No JSON data received"})

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
    app.run(host='0.0.0.0', port=8000)