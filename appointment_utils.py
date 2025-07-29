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

def save_user_memory(phone, memory):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_memory (
        phone TEXT PRIMARY KEY,
        memory TEXT
    )''')
    import json
    c.execute('REPLACE INTO user_memory (phone, memory) VALUES (?, ?)', (phone, json.dumps(memory)))
    conn.commit()
    conn.close()

def load_user_memory(phone):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_memory (
        phone TEXT PRIMARY KEY,
        memory TEXT
    )''')
    c.execute('SELECT memory FROM user_memory WHERE phone = ?', (phone,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        import json
        return json.loads(row[0])
    return [] 