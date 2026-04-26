import sqlite3

conn = sqlite3.connect("data/churn_mlops.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM model_registry")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
