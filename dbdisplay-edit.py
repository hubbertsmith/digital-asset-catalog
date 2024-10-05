# licensed under terms of MIT License -- Copyright (c) 2024 i4 Ops, inc. and hubbert Smith  

import psycopg2
import PySimpleGUI as sg
from psycopg2 import sql
from datetime import datetime

# Database connection parameters
db_params = {
    'dbname': 'i4catalog-v1',
    'user': 'hubbert',
    'password': 'u0',
    'host': 'u0',
    'port': 5432
}

# Global settings
FONT = ("Helvetica", 18)
BUTTON_FONT = ("Helvetica", 16)
sg.set_options(font=FONT)

def connect_to_db():
    return psycopg2.connect(**db_params)

def fetch_table_data(table_name):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
    columns = [desc[0] for desc in cur.description]
    data = cur.fetchall()
    cur.close()
    conn.close()
    return columns, data

def update_record(table_name, primary_key, primary_key_value, updates):
    conn = connect_to_db()
    cur = conn.cursor()
    update_query = sql.SQL("UPDATE {} SET {} WHERE {} = %s").format(
        sql.Identifier(table_name),
        sql.SQL(', ').join(map(lambda k: sql.SQL("{} = %s").format(sql.Identifier(k)), updates.keys())),
        sql.Identifier(primary_key)
    )
    cur.execute(update_query, list(updates.values()) + [primary_key_value])
    conn.commit()
    cur.close()
    conn.close()

def insert_record(table_name, values):
    conn = connect_to_db()
    cur = conn.cursor()
    insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(table_name),
        sql.SQL(', ').join(map(sql.Identifier, values.keys())),
        sql.SQL(', ').join(sql.Placeholder() * len(values))
    )
    cur.execute(insert_query, list(values.values()))
    conn.commit()
    cur.close()
    conn.close()

def delete_record(table_name, primary_key, primary_key_value):
    conn = connect_to_db()
    cur = conn.cursor()
    delete_query = sql.SQL("DELETE FROM {} WHERE {} = %s").format(
        sql.Identifier(table_name),
        sql.Identifier(primary_key)
    )
    cur.execute(delete_query, [primary_key_value])
    conn.commit()
    cur.close()
    conn.close()

def create_layout(table_name, columns, data):
    layout = [
        [sg.Text(f"Table: {table_name}", font=("Helvetica", 24))],
        [sg.Table(values=data, headings=columns, display_row_numbers=False, auto_size_columns=False, 
                  num_rows=min(25, len(data)), key='-TABLE-', font=FONT, col_widths=[max(len(str(col)), 20) for col in columns])],
        [sg.Button("Edit", font=BUTTON_FONT), sg.Button("Add Row", font=BUTTON_FONT), sg.Button("Delete Row", font=BUTTON_FONT),
         sg.Button("Refresh", font=BUTTON_FONT), sg.Button("Back", font=BUTTON_FONT)]
    ]
    return layout

def create_edit_layout(columns, values):
    layout = [[sg.Text(col, size=(20,1)), sg.Input(str(values[i]) if values[i] is not None else '', key=col, font=FONT, size=(30,1))] for i, col in enumerate(columns)]
    layout.append([sg.Button("Save", font=BUTTON_FONT), sg.Button("Cancel", font=BUTTON_FONT)])
    return layout

def create_window(title, layout, size=(1200, 800)):
    return sg.Window(title, layout, resizable=True, finalize=True, location=(50, 50), size=size)

def main():
    tables = ['asset-0', 'asset-event', 'policy-0', 'policy-event']
    
    main_layout = [[sg.Text("Select a table:", font=FONT), sg.Combo(tables, key='-TABLE-', enable_events=True, font=FONT, size=(30,1))]]
    window = create_window("Database Editor", main_layout, size=(800, 150))

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == '-TABLE-':
            table_name = values['-TABLE-']
            columns, data = fetch_table_data(table_name)
            window.close()
            window = create_window("Table View", create_layout(table_name, columns, data))
        elif event == "Edit":
            if len(values['-TABLE-']) == 0:
                sg.popup("Please select a row to edit.", font=FONT)
                continue
            row_index = values['-TABLE-'][0]
            edit_window = create_window("Edit Record", create_edit_layout(columns, data[row_index]), size=(1000, 600))
            while True:
                edit_event, edit_values = edit_window.read()
                if edit_event in (sg.WINDOW_CLOSED, "Cancel"):
                    break
                if edit_event == "Save":
                    updates = {col: edit_values[col] for col in columns[1:]}  # Exclude primary key
                    primary_key = columns[0]
                    primary_key_value = data[row_index][0]
                    update_record(table_name, primary_key, primary_key_value, updates)
                    sg.popup("Record updated successfully!", font=FONT)
                    break
            edit_window.close()
        elif event == "Add Row":
            add_window = create_window("Add Record", create_edit_layout(columns, [''] * len(columns)), size=(1000, 600))
            while True:
                add_event, add_values = add_window.read()
                if add_event in (sg.WINDOW_CLOSED, "Cancel"):
                    break
                if add_event == "Save":
                    new_record = {col: add_values[col] for col in columns if add_values[col]}
                    insert_record(table_name, new_record)
                    sg.popup("Record added successfully!", font=FONT)
                    break
            add_window.close()
        elif event == "Delete Row":
            if len(values['-TABLE-']) == 0:
                sg.popup("Please select a row to delete.", font=FONT)
                continue
            row_index = values['-TABLE-'][0]
            primary_key = columns[0]
            primary_key_value = data[row_index][0]
            if sg.popup_yes_no("Are you sure you want to delete this record?", font=FONT) == "Yes":
                delete_record(table_name, primary_key, primary_key_value)
                sg.popup("Record deleted successfully!", font=FONT)
        elif event == "Refresh":
            columns, data = fetch_table_data(table_name)
            window.close()
            window = create_window("Table View", create_layout(table_name, columns, data))
        elif event == "Back":
            window.close()
            window = create_window("Database Editor", main_layout, size=(800, 150))

    window.close()

if __name__ == "__main__":
    main()
