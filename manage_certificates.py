import os
import sqlite3
from datetime import datetime, timedelta
import subprocess

DB_PATH = '/etc/ssl/certificate_info.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY,
            domain TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def create_certificates():
    domain = os.environ.get('DOMAIN')
    subprocess.run([
        "openssl", "req", "-x509", "-nodes", "-days", "90", "-newkey", "rsa:2048",
        "-keyout", f"/etc/ssl/private/{domain}.key",
        "-out", f"/etc/ssl/certs/{domain}.crt",
        "-subj", f"/CN={domain}"
    ])
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO certificates (domain, created_at) VALUES (?, ?)', (domain, datetime.now()))
    conn.commit()
    conn.close()

def check_and_create_certificates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT created_at FROM certificates ORDER BY created_at DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()

    if row:
        created_at = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        if datetime.now() > created_at + timedelta(days=75):
            create_certificates()
    else:
        create_certificates()

if __name__ == "__main__":
    init_db()
    check_and_create_certificates()
