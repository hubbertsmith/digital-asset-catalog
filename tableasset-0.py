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
table_name = 'asset-0'
columns = [
    ('asset_id', 'SERIAL PRIMARY KEY'),
    ('asset_name', 'VARCHAR(255)'),
    ('asset_oversight', 'VARCHAR(255)'),
    ('asset_owner', 'VARCHAR(255)'),
    ('policy', 'VARCHAR(255)'),
    ('born_on', 'DATE'),
    ('decommission', 'DATE'),
    ('notes', 'TEXT'),
    ('blob', 'BYTEA')
]

# SQL command to create the table
create_table_command = sql.SQL("""
    CREATE TABLE IF NOT EXISTS {} (
        {}
    )
""").format(
    sql.Identifier(table_name),
    sql.SQL(', ').join(
        sql.SQL("{} {}").format(sql.Identifier(name), sql.SQL(type_))
        for name, type_ in columns
    )
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