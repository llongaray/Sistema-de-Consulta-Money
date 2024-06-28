from django.urls import path
from . import views

app_name = 'siape'

urlpatterns = [
    path('consulta-cliente/', views.consulta_cliente, name='consulta_cliente'),
    path('consulta-cliente/ficha-cliente/<str:cpf_cliente>/', views.ficha_cliente, name='ficha_cliente_cpf'),
]
