from django.contrib import admin

# Register your models here.
# apps/funcionarios/admin.py
from django.contrib import admin
from .models import Ranking, RegisterMoney, RegisterMeta

@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'setor', 'localidade')
    search_fields = ('nome_completo', 'cpf', 'setor')

@admin.register(RegisterMoney)
class RegisterMoneyAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'cpf_cliente', 'valor_est', 'status', 'data')
    list_filter = ('status', 'data')
    search_fields = ('funcionario__nome_completo', 'cpf_cliente')

@admin.register(RegisterMeta)
class RegisterMetaAdmin(admin.ModelAdmin):
    list_display = ('titulo','valor', 'setor', 'range_data_inicio', 'range_data_final', 'status', 'descricao')
    list_filter = ('setor', 'status')
    search_fields = ('setor', 'descricao')
