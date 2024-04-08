from django.urls import path
from . import views

app_name = 'RescueOperations'

urlpatterns = [

    path('', views.index, name='index'),
    path('login', views.login_view, name='login_view'),
    path('dashboard', views.Dashboard, name='Dashboard'),
    path('deviceDashboard', views.deviceDashboard, name='deviceDashboard'),
    path('logout', views.logout_view, name='logout_view'),
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('generate_csv/', views.generate_csv, name='generate_csv'),
]