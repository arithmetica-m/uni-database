
import sqlite3

connection = sqlite3.connect("example.db")

# Create a table.
connection.execute("""
    CREATE TABLE IF NOT EXISTS University (
        university_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        city TEXT,
    )
""")

# Add a record.
connection.execute(
    "INSERT INTO University (name, city) VALUES (?, ?)",
    ("Example University", "Munich")
)
connection.commit()

# Read the records.
rows = connection.execute(
    "SELECT * FROM University"
).fetchall()

for row in rows:
    print(row)

connection.close()