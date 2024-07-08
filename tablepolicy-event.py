# licensed under terms of MIT License -- Copyright (c) 2024 i4 Ops, inc. and hubbert Smith 
import psycopg2
from psycopg2 import sql

# Database connection parameters
db_params = {
    'dbname': 'i4catalog-v1',
    'user': 'hubbert',
    'password': 'u5',
    'host': 'u5',
    'port': 5432
}

# Table name and column definitions
table_name = 'policy-event'
columns = [
    ('id', 'SERIAL PRIMARY KEY'),
    ('policy_id', 'INTEGER'),
    ('event', 'VARCHAR(255)'),
    ('signoff', 'VARCHAR(255)'),
    ('date', 'DATE'),
    ('notes', 'TEXT'),
    ('blob', 'BYTEA')
]

# SQL command to create the table
create_table_command = sql.SQL("""
    CREATE TABLE IF NOT EXISTS {} (
        {},
        FOREIGN KEY (policy_id) REFERENCES {}(policy_id)
    )
""").format(
    sql.Identifier(table_name),
    sql.SQL(', ').join(
        sql.SQL("{} {}").format(sql.Identifier(name), sql.SQL(type_))
        for name, type_ in columns
    ),
    sql.Identifier("policy-0")  # Reference to the policy-0 table
)

try:
    # Connect to the database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Execute the create table command
    cursor.execute(create_table_command)

    # Commit the changes
    conn.commit()

    print(f"Table '{table_name}' created successfully.")

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL or creating table:", error)

finally:
    # Close the database connection
    if conn:
        cursor.close()
        conn.close()
        print("PostgreSQL connection is closed")
        
