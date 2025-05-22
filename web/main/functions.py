import csv
import io
import sqlite3
from pathlib import Path
from django.conf import settings
import subprocess
import os
import re
import codecs


INVALID_MESSAGE = 'Invalid characters in table name. Table names can only consists of letters, numbers and underscores'

def generate_db_path(filename):
    """
    Creates the filepath str for the filename.
    """
    return str(Path.joinpath(Path(settings.BASE_DIR), 'temp_dbs', f'{filename}.db'))


def check_for_db(filename):
    """
    Checks if database exists using filename without extension.
    """
    return True if os.path.exists(generate_db_path(filename)) else False


def create_db(filename):
    """
    Creates a sqlite3 file.
    """
    if check_for_db(filename):
        return 'File already exists, please choose another name.'
    else:
        result = subprocess.run(['touch', generate_db_path(filename)])
        if result.returncode == 0:
            return 0
        else:
            return 'Something went wrong creating your file. Please try again'


def connect_to_db(filename):
    """
    Connects to the give sql
    """
    if not check_for_db(filename):
        return f'{filename} does not exist.'
    else:
        connection = sqlite3.connect(generate_db_path(filename))
        connection.row_factory = return_dict
        cursor = connection.cursor()
        return connection, cursor
    

def return_dict(cursor, row):
    """
    Converts the sqlite result from a tuple of values to a dictionary
    """
    row_dict = {}
    for index, column in enumerate(cursor.description):
        row_dict[column[0]] = row[index]
    return row_dict


def execute_query(filename, query, params=None):
    """
    Executes the query and returns the result message.
    """
    try:
        connection, cursor = connect_to_db(filename)
        cursor.execute(query, params) if params else cursor.execute(query)
        connection.commit()
        results = cursor.fetchall()
        message = cursor.rowcount
    except sqlite3.Error as error:
        message = error
        results = None
    cursor.close()
    connection.close()
    return results, message


def validate_identifiers(identifiers:list):
    """
    Validates that an identifier has only permissible characters to prevent against
    injection attack.
    """
    for identifier in identifiers:
        if identifier:
            if isinstance(identifier, list):
                for item in identifier:
                    if not re.match(r'^[A-Za-z0-9_]+$', item):
                        return False
            else:
                if not re.match(r'^[A-Za-z0-9_]+$', identifier):
                    return False
        else:
            return False
    return True


def create_table(filename, table_name):
    """
    Creates a table in the database.
    """
    if validate_identifiers([table_name]):
        query = f'CREATE TABLE {table_name} (row_id INTEGER PRIMARY KEY NOT NULL)'
        results, message = execute_query(filename, query)
        return results, message
    else:
        return None, INVALID_MESSAGE


def rename_table(filename, old_name, new_name):
    """
    Renames an existing table.
    """
    if not validate_identifiers([old_name, new_name]):
        return INVALID_MESSAGE
    query = f'ALTER TABLE {old_name} RENAME TO {new_name};'
    result, message = execute_query(filename, query)
    return result, message


def add_column(filename, table_name, column_name, datatype):
    """
    Adds a column to the table.
    """
    # Validate all identifiers before crafting the query
    if not validate_identifiers([table_name, column_name, datatype]):
        return None, INVALID_MESSAGE

    # Craft the query
    query = (
        f'ALTER TABLE {table_name} '
        f'ADD COLUMN {column_name} {datatype};'
    )
    results, message = execute_query(filename, query)
    return results, message


def insert_row(filename, table_name, data:dict):
    """
    Inserts the row into the table.
    data = {'column name': 'column value',}
    """
    # Validate table_name and column names
    if not validate_identifiers([table_name, list(data.keys())]):
        return None, INVALID_MESSAGE
    
    # Craft the query
    query = f'INSERT INTO {table_name} ({', '.join(list(data.keys()))}) VALUES('
    params = []
    for value in list(data.values()):
        params.append(value)
        query += '?, '
    query = query[:-2] + ');'
    results, message = execute_query(filename=filename, query=query, params=tuple(params))
    return results, message


def update_row_value(filename, table_name, column, row_id, value):
    """
    Updates a value in the table.
    """
    # Validate identifiers
    if not validate_identifiers([table_name, column]):
        return None, INVALID_MESSAGE
    query = (
        f'UPDATE {table_name} '
        f'SET {column} = ? '
        'WHERE row_id = ?;'
    )
    params = (value, row_id)
    results, message = execute_query(filename, query, params)
    return results, message


def delete_db(username):
    """
    """
    db_path = generate_db_path(username)
    if os.path.exists(db_path):
        subprocess.run(['rm', db_path])


def convert_csv(file_object, username):
    # Read the file
    filename = file_object.name
    # Check for coding type
    raw_data = file_object.read()
    if raw_data.startswith(codecs.BOM_UTF8):
        encoding = 'utf-8-sig'
    else:
        encoding = 'utf-8'
    # Reset reader
    file_object.seek(0)
    file_text = io.StringIO(file_object.read().decode(encoding))
    csv_object = csv.DictReader(file_text)
    unedited_rows = [line for line in csv_object]
    # unedited_columns = csv_object.fieldnames

    # Clean up columns
    replace_with_none = ['"', "'",]
    replace_with_underscore = ['!!', ')', '(', ',', ' ', '.', ';']
    rows = []
    for row in unedited_rows:
        row_dict = {}
        for key, value in row.items():
            for item in replace_with_none:
                key = key.replace(item, '')
            for item in replace_with_underscore:
                key = key.replace(item, '_')
            row_dict[key] = value
        rows.append(row_dict)
    columns = list(rows[0].keys())

    # Create the database
    create_db(username)
    # Create the table
    create_table(username, f'{username}_table')
    # Add the columns
    for column in columns:
        add_column(username, f'{username}_table', column, 'TEXT')
    # Insert the rows
    for row in rows:
        insert_row(username, f'{username}_table', row)
    # Return the table results
    return execute_query(
        username, 
        f'SELECT * FROM {username}_table;'
    )