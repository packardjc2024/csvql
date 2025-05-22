from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.index, name='index'),
    path('update_row_field/', views.update_row_field, name='update_row_field'),
    path('delete/', views.delete, name='delete'),
    path('import_csv/', views.import_csv, name='import_csv'),
    path('export/', views.export, name='export'),
    path('search/', views.search, name='search'),
    path('query', views.query, name='query'),
]
