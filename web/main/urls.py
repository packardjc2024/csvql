from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.index, name='index'),
    path('update_row_field/', views.update_row_field, name='update_row_field'),
]
