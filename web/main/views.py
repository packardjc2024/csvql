from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.db.models import F
from django.urls import reverse
from .models import *
from .functions import *


def index(request):
    """
    """
    if request.method == 'GET':
        context = {}
        num_columns = 5
        num_rows = 10
        counter = 1
        filename = ''

        # Create a new database file
        while True:
            if create_db(f'new_spreadsheet_{counter}') == 0:
                filename = f'new_spreadsheet_{counter}'
                break
            else:
                counter += 1

        # Create a "blank" table
        table_name = 'blank_table'
        results, message = create_table(filename, table_name)

        # Create generic columns
        columns = [chr(i + 64) for i in range(1, num_columns + 1)]
        for column in columns:
            results, message = add_column(filename, table_name, column, 'TEXT')

        # Create generic rows
        rows = [i for i in range(1, num_rows + 1)]
        for row in rows:
            row_dict = {column: None for column in columns}
            results, message = insert_row(filename, table_name, row_dict)

        # temporary check table is created:
        query = f'select * from {table_name};'
        print(query)
        results, message = execute_query(filename, query)

        # Save the filename and table name as session variables
        request.session['filename'] = filename
        request.session['table_name'] = table_name

        # Add the rows and columns to the context
        context['columns'] = columns
        context['rows'] = rows

        # Render the initial blank spreadsheet
        return render(request, 'main/index.html', context)


def update_row_field(request):
    """
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'POST':
        row = request.POST['row']
        column = request.POST['column']
        value = request.POST['value']

        results, message = update_row_value(
            filename=request.session['filename'],
            table_name=request.session['table_name'],
            column=column.strip(),
            row_id=row,
            value=value
        )

        results, message = execute_query(
            request.session['filename'],
            'select * from blank_table;'                       
        )
        print(results)

        return JsonResponse({'result': 0}, status=200)
    return JsonResponse({'result': 1}, status=400)
