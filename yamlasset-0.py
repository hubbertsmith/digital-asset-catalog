# licensed under terms of MIT License -- Copyright (c) 2024 i4 Ops, inc. and hubbert Smith 
import psycopg2
from psycopg2 import sql
import yaml

# Database connection parameters
db_params = {
    'dbname': 'i4catalog-v1',
    'user': 'hubbert',
    'password': 'u5',
    'host': 'u5',
    'port': 5432
}

def insert_asset(cursor, asset):
    insert_query = sql.SQL("""
        INSERT INTO "asset-0" (asset_name, asset_oversight, asset_owner, policy, born_on, decommission, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING asset_id
    """)
    
    cursor.execute(insert_query, (
        asset.get('asset_name'),
        asset.get('asset_oversight'),
        asset.get('asset_owner'),
        asset.get('policy'),
        asset.get('born_on'),
        asset.get('decommission'),
        asset.get('notes')
    ))
    
    return cursor.fetchone()[0]

def main():
    # Load data from YAML file
    with open('yamlasset-0.yaml', 'r') as file:
        assets_data = yaml.safe_load(file)

    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Insert each asset
        for asset in assets_data['assets']:
            asset_id = insert_asset(cursor, asset)
            print(f"Inserted asset with ID: {asset_id}")

        # Commit the changes
        conn.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL or inserting data:", error)
        conn.rollback()

    finally:
        # Close the database connection
        if conn:
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")

if __name__ == "__main__":
    main()

