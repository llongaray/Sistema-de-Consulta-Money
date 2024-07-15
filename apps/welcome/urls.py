from django.urls import path
from . import views

app_name = "welcome"

urlpatterns = [
    path('', views.welcome, name="welcome"),
    path('log/', views.log, name="log"),
    path('cad/', views.cad, name="cad"),
]
