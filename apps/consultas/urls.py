from django.urls import path
from . import views

app_name = 'consulta'  # Corrigido para 'consulta'

urlpatterns = [
    path('gerenciamento/', views.gerenciamento, name='gerenciamento'),
    path('consulta-cliente/', views.consulta_cliente, name='consulta_cliente'),
    path('ficha-cliente/<str:cpf_cliente>/', views.ficha_cliente, name='ficha_cliente_cpf'),
]
