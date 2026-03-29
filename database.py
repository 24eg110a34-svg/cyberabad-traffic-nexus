"""
CYBERABAD TRAFFIC NEXUS - SQLite Database Module
Stores traffic data, predictions, alerts, and system logs
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'traffic_data.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Traffic readings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            junction_id INTEGER,
            junction_name TEXT,
            area TEXT,
            vehicle_count INTEGER,
            score REAL,
            situation TEXT,
            speed REAL,
            delay REAL,
            weather TEXT,
            is_holiday INTEGER DEFAULT 0,
            day_of_week INTEGER
        )
    ''')
    
    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            car_count INTEGER,
            bike_count INTEGER,
            bus_count INTEGER,
            truck_count INTEGER,
            hour INTEGER,
            day_of_week INTEGER,
            is_holiday INTEGER,
            is_raining INTEGER,
            prediction TEXT,
            confidence REAL,
            score REAL,
            speed REAL,
            delay REAL,
            encrypted_data TEXT
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            alert_type TEXT,
            severity TEXT,
            location TEXT,
            area TEXT,
            score REAL,
            message TEXT,
            action TEXT,
            acknowledged INTEGER DEFAULT 0,
            nlp_sentiment REAL,
            nlp_keywords TEXT
        )
    ''')
    
    # Face recognition logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            camera_id TEXT,
            person_count INTEGER,
            helmet_violations INTEGER,
            mobile_violations INTEGER,
            face_encoding BLOB,
            confidence REAL
        )
    ''')
    
    # Weather data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            condition TEXT,
            temperature REAL,
            humidity REAL,
            wind_speed REAL,
            visibility REAL,
            rain_probability REAL,
            impact_score REAL,
            source TEXT
        )
    ''')
    
    # System logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            log_level TEXT,
            module TEXT,
            message TEXT,
            details TEXT
        )
    ''')
    
    # Emergency events
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emergency_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT,
            route TEXT,
            affected_junctions TEXT,
            status TEXT,
            eta_minutes INTEGER,
            vehicle_id TEXT
        )
    ''')
    
    # Green wave routes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS green_wave_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            route_name TEXT,
            segments TEXT,
            junctions TEXT,
            optimal_speed INTEGER,
            is_active INTEGER DEFAULT 0,
            travel_time_saved REAL,
            stops_reduced INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def log_traffic_reading(junction_id, junction_name, area, vehicle_count, score, situation, speed, delay, weather, is_holiday, day_of_week):
    """Log a traffic reading"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO traffic_readings 
        (junction_id, junction_name, area, vehicle_count, score, situation, speed, delay, weather, is_holiday, day_of_week)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (junction_id, junction_name, area, vehicle_count, score, situation, speed, delay, weather, int(is_holiday), day_of_week))
    conn.commit()
    reading_id = cursor.lastrowid
    conn.close()
    return reading_id

def save_prediction(car_count, bike_count, bus_count, truck_count, hour, day_of_week, is_holiday, is_raining, prediction, confidence, score, speed, delay, encrypted_data=None):
    """Save a prediction"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions 
        (car_count, bike_count, bus_count, truck_count, hour, day_of_week, is_holiday, is_raining, prediction, confidence, score, speed, delay, encrypted_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (car_count, bike_count, bus_count, truck_count, hour, day_of_week, int(is_holiday), int(is_raining), prediction, confidence, score, speed, delay, encrypted_data))
    conn.commit()
    pred_id = cursor.lastrowid
    conn.close()
    return pred_id

def save_alert(alert_type, severity, location, area, score, message, action, nlp_sentiment=0.5, nlp_keywords=""):
    """Save an alert"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alerts 
        (alert_type, severity, location, area, score, message, action, nlp_sentiment, nlp_keywords)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (alert_type, severity, location, area, score, message, action, nlp_sentiment, nlp_keywords))
    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    return alert_id

def save_face_log(camera_id, person_count, helmet_violations, mobile_violations, confidence):
    """Save face recognition log"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO face_logs 
        (camera_id, person_count, helmet_violations, mobile_violations, confidence)
        VALUES (?, ?, ?, ?, ?)
    ''', (camera_id, person_count, helmet_violations, mobile_violations, confidence))
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id

def save_weather(condition, temperature, humidity, wind_speed, visibility, rain_prob, impact_score, source="API"):
    """Save weather data"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO weather_data 
        (condition, temperature, humidity, wind_speed, visibility, rain_probability, impact_score, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (condition, temperature, humidity, wind_speed, visibility, rain_prob, impact_score, source))
    conn.commit()
    weather_id = cursor.lastrowid
    conn.close()
    return weather_id

def log_event(log_level, module, message, details=None):
    """Log system event"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO system_logs (log_level, module, message, details)
        VALUES (?, ?, ?, ?)
    ''', (log_level, module, message, json.dumps(details) if details else None))
    conn.commit()
    conn.close()

def get_recent_readings(hours=24, area=None, junction_id=None):
    """Get recent traffic readings"""
    conn = get_db()
    cursor = conn.cursor()
    
    since = datetime.now() - timedelta(hours=hours)
    query = 'SELECT * FROM traffic_readings WHERE timestamp >= ?'
    params = [since]
    
    if area:
        query += ' AND area = ?'
        params.append(area)
    if junction_id:
        query += ' AND junction_id = ?'
        params.append(junction_id)
    
    query += ' ORDER BY timestamp DESC'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_predictions_history(limit=100):
    """Get prediction history"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_alerts_history(severity=None, limit=100):
    """Get alerts history"""
    conn = get_db()
    cursor = conn.cursor()
    
    if severity:
        cursor.execute('SELECT * FROM alerts WHERE severity = ? ORDER BY timestamp DESC LIMIT ?', (severity, limit))
    else:
        cursor.execute('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_weather_history(hours=24):
    """Get weather history"""
    conn = get_db()
    cursor = conn.cursor()
    since = datetime.now() - timedelta(hours=hours)
    cursor.execute('SELECT * FROM weather_data WHERE timestamp >= ? ORDER BY timestamp DESC', (since,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_analytics_summary():
    """Get analytics summary"""
    conn = get_db()
    cursor = conn.cursor()
    
    summary = {}
    
    cursor.execute('SELECT COUNT(*) as total FROM traffic_readings')
    summary['total_readings'] = cursor.fetchone()['total']
    
    cursor.execute('SELECT AVG(score) as avg_score FROM traffic_readings WHERE timestamp >= ?', 
                   (datetime.now() - timedelta(hours=24),))
    summary['avg_score_24h'] = cursor.fetchone()['avg_score'] or 0
    
    cursor.execute('SELECT COUNT(*) as total FROM predictions')
    summary['total_predictions'] = cursor.fetchone()['total']
    
    cursor.execute('SELECT AVG(confidence) as avg_conf FROM predictions')
    summary['avg_confidence'] = cursor.fetchone()['avg_conf'] or 0
    
    cursor.execute('SELECT COUNT(*) as total FROM alerts WHERE acknowledged = 0')
    summary['pending_alerts'] = cursor.fetchone()['total']
    
    cursor.execute('SELECT area, AVG(score) as avg_score, COUNT(*) as count FROM traffic_readings WHERE timestamp >= ? GROUP BY area',
                   (datetime.now() - timedelta(hours=24),))
    summary['area_stats'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return summary

def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE alerts SET acknowledged = 1 WHERE id = ?', (alert_id,))
    conn.commit()
    conn.close()

def save_emergency_event(event_type, route, affected_junctions, status, eta_minutes, vehicle_id):
    """Save emergency event"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emergency_events 
        (event_type, route, affected_junctions, status, eta_minutes, vehicle_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (event_type, route, json.dumps(affected_junctions), status, eta_minutes, vehicle_id))
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    return event_id

def save_green_wave(route_name, segments, junctions, optimal_speed, is_active, travel_time_saved, stops_reduced):
    """Save green wave route"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO green_wave_routes 
        (route_name, segments, junctions, optimal_speed, is_active, travel_time_saved, stops_reduced)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (route_name, json.dumps(segments), json.dumps(junctions), optimal_speed, int(is_active), travel_time_saved, stops_reduced))
    conn.commit()
    route_id = cursor.lastrowid
    conn.close()
    return route_id

# Initialize database on import
init_db()
