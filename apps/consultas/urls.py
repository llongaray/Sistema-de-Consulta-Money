from django.urls import path, include
from .views import gerencimento

app_name = "consultas"

urlpatterns = [
    path('gerenciamento', gerencimento, name="gerenciamento"),
]
