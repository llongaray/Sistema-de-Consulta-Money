from django.urls import path, include
from .views import gerenciamento

app_name = "consultas"

urlpatterns = [
    path('gerenciamento', gerenciamento, name="gerenciamento"),
]
