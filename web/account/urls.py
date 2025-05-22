from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('', views.index, name='index'),
    path('login_page/', views.login_page, name='login_page'),
    path('logout_page/', views.logout_page, name='logout_page'),
]
