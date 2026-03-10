import sqlite3

conn = sqlite3.connect("depression.db")
cursor = conn.cursor()

print("---- Messages ----")
cursor.execute("SELECT * FROM Message")
messages = cursor.fetchall()
print(messages)

print("\n---- Analysis Results ----")
cursor.execute("SELECT * FROM Analysis_Result")
results = cursor.fetchall()
print(results)

conn.close()
