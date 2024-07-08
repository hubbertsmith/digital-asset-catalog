# licensed under terms of MIT License -- Copyright (c) 2024 i4 Ops, inc. and hubbert Smith 
import psycopg2
from psycopg2 import sql
import yaml
from datetime import datetime, date

# Database connection parameters
db_params = {
    'dbname': 'i4catalog-v1',
    'user': 'hubbert',
    'password': 'u5',
    'host': 'u5',
    'port': 5432
}

def insert_asset_event(cursor, event):
    insert_query = sql.SQL("""
        INSERT INTO "asset-event" (asset_id, event, location, signoff, date, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """)
    
    cursor.execute(insert_query, (
        event.get('asset_id'),
        event.get('event'),
        event.get('location'),
        event.get('signoff'),
        event.get('date'),
        event.get('notes')
    ))
    
    return cursor.fetchone()[0]

def main():
    # Load data from YAML file
    with open('yamlasset-event.yaml', 'r') as file:
        events_data = yaml.safe_load(file)

    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Insert each asset event
        for event in events_data['asset_events']:
            # Handle date field
            if 'date' in event and event['date']:
                if isinstance(event['date'], str):
                    event['date'] = datetime.strptime(event['date'], '%Y-%m-%d').date()
                elif isinstance(event['date'], date):
                    # If it's already a date object, no need to parse
                    pass
                else:
                    print(f"Unexpected date format for event: {event}")
                    continue
            
            event_id = insert_asset_event(cursor, event)
            print(f"Inserted asset event with ID: {event_id}")

        # Commit the changes
        conn.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL or inserting data:", error)
        if conn:
            conn.rollback()

    finally:
        # Close the database connection
        if conn:
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")

if __name__ == "__main__":
    main()
