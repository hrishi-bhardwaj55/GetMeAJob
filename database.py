import sqlite3
import threading
import os
import config

class Database:
    def __init__(self, db_file=config.DB_FILE):
        self.db_file = db_file
        self._lock = threading.Lock()
        self.conn = None
        self.cursor = None
        self._initialize_db()

    def _initialize_db(self):
        """Creates the database and tables if they don't exist."""
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_jobs (
                job_id TEXT PRIMARY KEY,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def is_job_processed(self, job_id):
        """Checks if a job_id already exists in the database."""
        with self._lock:
            self.cursor.execute('SELECT 1 FROM processed_jobs WHERE job_id = ?', (job_id,))
            return self.cursor.fetchone() is not None

    def mark_job_processed(self, job_id):
        """Inserts a job_id into the database to mark it as processed."""
        with self._lock:
            try:
                self.cursor.execute('INSERT INTO processed_jobs (job_id) VALUES (?)', (job_id,))
                self.conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()

# Singleton-like instantiation for easy import
db = Database()

