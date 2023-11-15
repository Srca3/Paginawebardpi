from flask import Flask, render_template, jsonify, request
import serial
import json
import sqlite3
from datetime import datetime
import random
from threading import Thread
import time

app = Flask(__name__)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)


def parse_serial_data():
    # Se espera que los datos estén en formato "PL:0.00,UV:0.00,TE:28.30,HU:58.00"
    data = ser.readline().decode('utf-8').strip()
    data_parts = data.split(',')
    
    
    data_dict = {}

    for part in data_parts:
        key, value = part.split(':')
        data_dict[key.lower()] = float(value)

    return data_dict


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
            radiacion_uv REAL,
            temperatura REAL,
            humedad REAL       
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
    #create_table()  # Crea la tabla antes de cada solicitud
    
    data_dict = parse_serial_data()

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO weather_data (lluvia, radiacion_uv, temperatura, humedad)
        VALUES (?, ?, ?, ?)
    ''', (data_dict['pl'], data_dict['uv'], data_dict['te'], data_dict['hu']))
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
    app.run(host='0.0.0.0', port=8000)