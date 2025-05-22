from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.db.models import F
from django.urls import reverse
from .models import *
from .functions import *
from io import StringIO


@login_required
def index(request):
    """
    """
    if request.method == 'GET':
        context = {}
        filename = request.user.username
        table_name = f'{request.user.username}_table'

        # Create a new database and table if one doesn't already exists:
        if not check_for_db(filename):
            num_columns = 5
            num_rows = 10
            create_db(filename)
            # Create a "blank" table
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

        # Query the table for the context        
        if validate_identifiers([table_name]):
            data, message = execute_query(filename, f'SELECT * FROM {table_name};')
            context['columns'] = list(data[0].keys())
            context['rows'] = data
            context['column_index'] = [i for i in range(1, len(context['columns']))]

        # Render the initial blank spreadsheet
        return render(request, 'main/index.html', context)


@login_required
def update_row_field(request):
    """
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'POST':
        if validate_identifiers([f'{request.user.username}_table']):
            results, message = update_row_value(
                filename=request.user.username,
                table_name=f'{request.user.username}_table',
                column=request.POST['column'],
                row_id=request.POST['row'],
                value=request.POST['value']
            )
            return JsonResponse({'result': 0}, status=200)
    return JsonResponse({'result': 1}, status=400)


@login_required
def delete(request):
    """
    """
    delete_db(request.user.username)
    return HttpResponseRedirect(reverse('main:index'))


@login_required
def import_csv(request):
    """
    """
    # Delete the current table
    delete_db(request.user.username)
    # Conver CSV to database
    if request.method == 'POST':
        file = request.FILES['csv-file']
        results, message = convert_csv(file, request.user.username)
        if not results:
            delete_db(request.user.username)
            print(message)
    print('SOMETHING WENT WRONG')
    return HttpResponseRedirect(reverse('main:index'))


@login_required
def export(request):
    """
    """
    if validate_identifiers(request.user.username):
        rows, message = execute_query(
            request.user.username,
            f'SELECT * FROM {request.user.username}_table;'
        )
        columns = list(rows[0].keys())

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=csvql_table.csv'
        writer = csv.writer(response)
        writer.writerow(columns)
        for row in rows:
            writer.writerow(list(row.values()))
        return response


@login_required
def query(request):
    """
    """
    pass


@login_required
def search(request):
    """
    """
    pass