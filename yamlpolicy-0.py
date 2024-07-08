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

def insert_policy(cursor, policy):
    insert_query = sql.SQL("""
        INSERT INTO "policy-0" (policy, policy_oversight, policy_owner, signoff, date, decommission, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING policy_id
    """)
    
    cursor.execute(insert_query, (
        policy.get('policy'),
        policy.get('policy_oversight'),
        policy.get('policy_owner'),
        policy.get('signoff'),
        policy.get('date'),
        policy.get('decommission'),
        policy.get('notes')
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
    with open('yamlpolicy-0.yaml', 'r') as file:
        policies_data = yaml.safe_load(file)

    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Insert each policy
        for policy in policies_data['policies']:
            # Convert date strings to datetime objects
            for date_field in ['date', 'decommission']:
                if date_field in policy:
                    try:
                        policy[date_field] = parse_date(policy[date_field])
                    except ValueError as e:
                        print(f"Error parsing {date_field} for policy: {e}")
                        print(f"Policy data: {policy}")
                        continue
            
            try:
                policy_id = insert_policy(cursor, policy)
                print(f"Inserted policy with ID: {policy_id}")
            except Exception as e:
                print(f"Error inserting policy: {e}")
                print(f"Policy data: {policy}")

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

