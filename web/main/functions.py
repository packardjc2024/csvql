import csv
import io
import sqlite3
from pathlib import Path
from django.conf import settings
import subprocess
import os
import re


INVALID_MESSAGE = 'Invalid characters in table name. Table names can only consists of letters, numbers and underscores'

def generate_db_path(filename):
    """
    Creates the filepath str for the filename.
    """
    return str(Path.joinpath(Path(settings.BASE_DIR), 'temp_dbs', f'{filename}.db'))


def check_for_db(filename):
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
        cursor = connection.cursor()
        return connection, cursor
    

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


def convert_csv(file_object, filename: str, username: str):
    # Read the file
    file_text = io.StringIO(file_object.read().decode('utf-8'))
    csv_object = csv.DictReader(file_text)
    rows = [line for line in csv_object]
    columns = csv_object.fieldnames

    # format the data
    table_name = filename.strip().lower().replace('.csv', '').replace(' ', '_')
    columns_list = [f'{column.strip().lower().replace(' ', '_').replace(',', '')} text' for column in columns]
    columns_string = ', '.join(columns_list)
    rows_list = [', '.join(row.values()) for row in rows]
    rows_string = '), '.join(rows_list)

    # Create temporary sqlite file
    db_path = Path.joinpath(Path(settings.BASE_DIR), 'temp_dbs', f'{username}.db')
    delete_db(username)
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(f'DROP TABLE IF EXISTS {table_name};')
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_string});')
    for row in rows:
        paramaters = ['?'] * len(rows[0].values())
        cursor.execute(f'INSERT INTO {table_name} VALUES({', '.join(paramaters)});', (list(row.values())))
    connection.commit()
    return table_name


def query_db(query, username, session_table):
    """
    """
    try:
        table_name = re.search(r'from\s+(\w+)', query, re.IGNORECASE).group(1)
    except:
        table_name = session_table
    db_path = Path.joinpath(Path(settings.BASE_DIR), 'temp_dbs', f'{username}.db')
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        message = f'SUCCESS: {len(rows)} rows returned.'
        return rows, columns, table_name, message
    except sqlite3.Error as error:
        return None, None, None, f'SQL ERROR: {error}.'


def delete_db(username):
    """
    """
    db_path = Path.joinpath(Path(settings.BASE_DIR), 'temp_dbs', f'{username}.db')
    if os.path.exists(db_path):
        subprocess.run(['rm', str(db_path)])
        # logger.info('Users temp_db deleted')
    else:
        # logger.info('no user db existed')
        pass


