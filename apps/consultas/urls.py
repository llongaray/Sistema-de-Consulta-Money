from django.urls import path
from . import views

app_name = "consultas"

urlpatterns = [
    path('', views.consultas, name="consultas")
]
