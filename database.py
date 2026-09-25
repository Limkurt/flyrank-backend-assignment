import sqlite3 # TO REMOVE
import psycopg
from dotenv import load_dotenv
import os

# Load variable from .env into os.environ
load_dotenv()

DB_PATH = os.getenv("DATABASE_URL")

#Dummy data
DATA = [
  { "id": 1, "title": "Draw", "done": False}, 
  { "id": 2, "title": "Watch", "done": False},
  { "id": 3, "title": "Listen", "done": False}
]

def get_db():
  return psycopg.connect(DB_PATH)

def init_db():
  with get_db() as con:
    with con.cursor() as cur:

      cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
          id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
          title TEXT,
          DONE BOOLEAN
        );
      """)

      # Insert Inquiry
      cur.execute("SELECT EXISTS(SELECT 1 FROM tasks)")
      is_empty = cur.fetchone()[0] == 0 # Checks if table has data

      if is_empty:
        for item in DATA:
          cur.execute(
            """
            INSERT INTO tasks (title, done)
            VALUES (%s, %s)
            """,
            (item["title"], item["done"])
          )