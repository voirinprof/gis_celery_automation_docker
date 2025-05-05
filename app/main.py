from flask import Flask, render_template, request, jsonify
from tasks import compute_buffers_task
import sqlite3
import os

app = Flask(__name__)

# Chemin de la base de données
DB_PATH = '/root/db/points.db'

# Connexion à SQLite
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS points 
                 (id INTEGER PRIMARY KEY, lat REAL, lon REAL, radius INTEGER)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_point', methods=['POST'])
def add_point():
    data = request.json
    lat, lon, radius = data['lat'], data['lon'], data['radius']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO points (lat, lon, radius) VALUES (?, ?, ?)", (lat, lon, radius))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/get_points', methods=['GET'])
def get_points():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT lat, lon, radius FROM points")
    points = [{"lat": row[0], "lon": row[1], "radius": row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(points)

@app.route('/compute_buffers', methods=['POST'])
def compute_buffers():
    result = compute_buffers_task.delay()
    return jsonify({"task_id": result.id})

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    if result.state == 'PENDING':
        response = {'state': result.state, 'status': 'En attente...'}
    elif result.state == 'SUCCESS':
        response = {'state': result.state, 'buffers': result.get()}
    else:
        response = {'state': result.state, 'status': str(result.info)}
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)