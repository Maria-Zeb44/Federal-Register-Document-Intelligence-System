import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from src.core.config import config

class Database:
    def __init__(self):
        self.conn_string = config.DATABASE_URL
    
    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(self.conn_string)
        conn.autocommit = True  # ← FIX: Auto-commit every statement
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                return cur.rowcount
    
    def execute_one(self, query: str, params: tuple = None):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchone()