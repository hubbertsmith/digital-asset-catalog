import psycopg2
from psycopg2 import sql

# Database connection parameters
DB_PARAMS = {
    'dbname': 'i4catalog-v1',
    'user': 'hubbert',
    'password': 'u5',
    'host': 'localhost',
    'port': '5432'
}

def connect_to_database():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("Connected successfully to the i4catalog-v1 database!")
        return conn
    except psycopg2.Error as e:
        print(f"Unable to connect to the database: {e}")
        return None

def get_tables(cursor):
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    return [table[0] for table in cursor.fetchall()]

def get_table_columns(cursor, table_name):
    cursor.execute(sql.SQL("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = {}
        ORDER BY ordinal_position
    """).format(sql.Literal(table_name)))
    return [col[0] for col in cursor.fetchall()]

def get_table_data(cursor, table_name):
    cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
    return cursor.fetchall()

def write_table_data(file, table_name, columns, data):
    file.write(f"\n\n## Table: {table_name}\n\n")
    
    if not data:
        file.write("*No data in this table*\n")
        return
    
    # Calculate column widths
    col_widths = [max(len(str(col)), max((len(str(row[i])) if row[i] is not None else 4) for row in data)) for i, col in enumerate(columns)]
    
    # Write column headers
    header = "| " + " | ".join(f"{col:<{width}}" for col, width in zip(columns, col_widths)) + " |"
    file.write(header + "\n")
    file.write("|" + "|".join("-" * (width + 2) for width in col_widths) + "|\n")
    
    # Write data rows
    for row in data:
        formatted_row = [str(cell) if cell is not None else 'NULL' for cell in row]
        row_str = "| " + " | ".join(f"{cell:<{width}}" for cell, width in zip(formatted_row, col_widths)) + " |"
        file.write(row_str + "\n")

def main():
    conn = connect_to_database()
    if not conn:
        return

    try:
        with open('i4catalog_data_report.md', 'w') as file:
            with conn.cursor() as cursor:
                tables = get_tables(cursor)
                
                file.write("# Data Report for i4catalog-v1 Database\n")
                
                for table in tables:
                    try:
                        columns = get_table_columns(cursor, table)
                        data = get_table_data(cursor, table)
                        write_table_data(file, table, columns, data)
                    except Exception as e:
                        print(f"Error processing table {table}: {e}")
                        file.write(f"\n\n## Table: {table}\n\n")
                        file.write(f"*Error processing this table: {e}*\n")
                
        print("Data report has been written to i4catalog_data_report.md")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()

