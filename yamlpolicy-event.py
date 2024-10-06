# licensed under terms of MIT License -- Copyright (c) 2024 i4 Ops, inc. and hubbert Smith 
import psycopg2
from psycopg2 import sql
import yaml
from datetime import datetime, date

# Database connection parameters
db_params = {
    'dbname': 'i4catalog-v1',
    'user': 'hubbert',
    'password': 'u0',
    'host': 'u0',
    'port': 5432
}

def insert_policy_event(cursor, event):
    insert_query = sql.SQL("""
        INSERT INTO "policy-event" (policy_id, event, signoff, date, notes, tags)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """)
    
    cursor.execute(insert_query, (
        event.get('policy_id'),
        event.get('event'),
        event.get('signoff'),
        event.get('date'),
        event.get('notes')
        event.get('tags')
    ))
    
    return cursor.fetchone()[0]

def parse_date(date_value):
    if isinstance(date_value, str):
        return datetime.strptime(date_value, '%Y-%m-%d').date()
    elif isinstance(date_value, date):
        return date_value
    elif date_value is None:
        return None
    else:
        raise ValueError(f"Unexpected date format: {date_value}")

def main():
    # Load data from YAML file
    with open('yamlpolicy-event.yaml', 'r') as file:
        events_data = yaml.safe_load(file)

    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Insert each policy event
        for event in events_data['policy_events']:
            try:
                # Convert date string to datetime object
                if 'date' in event:
                    event['date'] = parse_date(event['date'])
                
                event_id = insert_policy_event(cursor, event)
                print(f"Inserted policy event with ID: {event_id}")
            except ValueError as e:
                print(f"Error parsing date for event: {e}")
                print(f"Event data: {event}")
            except Exception as e:
                print(f"Error inserting event: {e}")
                print(f"Event data: {event}")

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

