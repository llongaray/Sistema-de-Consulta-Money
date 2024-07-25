from django.db import models
from django.utils import timezone

# Create your models here.
class Ranking(models.Model):
    foto = models.ImageField(upload_to='img_colab/', blank=True, null=True)  # Recebe caminho relativo em 'media' para a foto do funcionário
    nome_completo = models.CharField(max_length=255)  # Recebe texto com nome completo (contendo espaços)
    cpf = models.CharField(max_length=11, unique=True)  # Recebe apenas números e tem que ser único
    setor = models.CharField(max_length=100)  # Recebe um Char
    localidade = models.CharField(max_length=255)  # Recebe um texto com a cidade (pode conter espaços)

    def __str__(self):
        return f'{self.nome_completo} - {self.cpf} - {self.setor}'

class RegisterMoney(models.Model):
    funcionario = models.ForeignKey('Ranking', on_delete=models.CASCADE, related_name='money_registers')
    cpf_cliente = models.CharField(max_length=11)
    valor_est = models.FloatField()
    status = models.BooleanField(default=False)
    data = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.funcionario} - {self.cpf_cliente} - {self.valor_est}'
