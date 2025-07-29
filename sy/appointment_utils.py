import sqlite3

def create_appointment(name, phone, datetime, notes):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('INSERT INTO appointments (name, phone, datetime, notes) VALUES (?, ?, ?, ?)', (name, phone, datetime, notes))
    conn.commit()
    conn.close()

def get_appointments():
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('SELECT * FROM appointments')
    results = c.fetchall()
    conn.close()
    return results 