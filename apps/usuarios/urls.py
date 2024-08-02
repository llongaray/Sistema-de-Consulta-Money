from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('auth/login/', views.login_index, name='login'),
    path('auth/register/', views.register_index, name='register'),
    path('auth/logout/', views.logout, name='logout'),
    path('dashboard/', views.welcome, name='welcome'),
]
