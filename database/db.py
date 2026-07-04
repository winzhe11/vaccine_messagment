import sqlite3
import os


class DB:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "vaccine_system.db")

        self.conn = None
        self.cursor = None
        self.db_path = db_path

        

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):


        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            users_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT,
            role TEXT NOT NULL
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS vaccines (
            batch_no TEXT PRIMARY KEY,
            vaccinename TEXT,
            manufacturer TEXT,
            vaccination_date TEXT,
            location TEXT,
            doses INTEGER,
            cost INTEGER,
            stock INTEGER
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            appointments_id INTEGER PRIMARY KEY AUTOINCREMENT,
            users_id INTEGER,
            batch_no TEXT,
            completed_doses INTEGER DEFAULT 0,              
            status TEXT DEFAULT '待确认',
            FOREIGN KEY (users_id) REFERENCES users(users_id),
            FOREIGN KEY (batch_no) REFERENCES vaccines(batch_no)                            
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS face_library (
            users_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            images_path TEXT NOT NULL,
            FOREIGN KEY (users_id) REFERENCES users(users_id)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS vaccine_info (
        vaccinename TEXT PRIMARY KEY,
        intro TEXT
        )
    """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_hospital (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            users_id TEXT NOT NULL,
            hospital_name TEXT NOT NULL,
            FOREIGN KEY (users_id) REFERENCES users(users_id)
        )
        """)


        self.conn.commit()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()