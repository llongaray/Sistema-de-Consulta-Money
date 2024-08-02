from django.db import models
from django.utils import timezone

class Ranking(models.Model):
    foto = models.ImageField(upload_to='img_colab/', blank=True, null=True)
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11, unique=True)
    setor = models.CharField(max_length=100)
    localidade = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.nome_completo} - {self.cpf} - {self.setor}'

class RegisterMoney(models.Model):
    funcionario = models.ForeignKey('Ranking', on_delete=models.CASCADE, related_name='money_registers')
    cpf_cliente = models.CharField(max_length=11, blank=True, null=True)
    valor_est = models.FloatField()
    status = models.BooleanField(default=False)
    data = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.funcionario} - {self.cpf_cliente} - {self.valor_est}'

class RegisterMeta(models.Model):
    titulo = models.TextField(max_length=100, default="Ranking Geral")
    valor = models.DecimalField(max_digits=10, decimal_places=2)  # Float com duas casas decimais (R$ {valor:.2f})
    setor = models.CharField(max_length=100)  # Não aceita espaços, apenas uma palavra
    range_data_inicio = models.DateField()  # Armazena o primeiro dia/data que a meta está valendo
    range_data_final = models.DateField()  # Armazena o dia/data final que a meta está valendo
    status = models.BooleanField(default=False)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.valor:.2f} - {self.setor}'

# Comentários foram adicionados explicando os campos e o método __str__ foi completado.
