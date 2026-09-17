import sqlite3

DB_PATH = "tasks.db"

#Dummy data
DATA = [
  { "id": 1, "title": "Draw", "done": False}, 
  { "id": 2, "title": "Watch", "done": False},
  { "id": 3, "title": "Listen", "done": False}
]

def get_db():
  return sqlite3.connect(DB_PATH)

def init_db():
  con = get_db()
  cur = con.cursor()

  cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT,
      DONE BOOLEAN
    );
  """)
  con.commit()

  # Insert Inquiry
  cur.execute("SELECT EXISTS(SELECT 1 FROM tasks)")
  is_empty = cur.fetchone()[0] == 0 # Checks if table has data

  if is_empty:
    for item in DATA:
      cur.execute(
        """
        INSERT INTO tasks (title, done)
        VALUES (?, ?)
        """,
        (item["title"], item["done"])
      )

    con.commit()
  con.close()