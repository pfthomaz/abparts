import psycopg2
import os

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="abparts_dev",
    user="abparts_user",
    password="abparts_password"
)

cur = conn.cursor()

# Check if machines table exists and has data
try:
    cur.execute("SELECT id, name, model_type FROM machines LIMIT 5;")
    machines = cur.fetchall()
    print(f"Found {len(machines)} machines:")
    for machine in machines:
        print(f"  ID: {machine[0]}, Name: {machine[1]}, Model: {machine[2]}")
except Exception as e:
    print(f"Error querying machines: {e}")

cur.close()
conn.close()