from django.urls import path
from .views import import_consultores

app_name = 'ranking'

urlpatterns = [
    path('importe-consultores/', import_consultores, name='import_consultores'),
]
