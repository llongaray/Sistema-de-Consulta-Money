from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11, unique=True)
    uf = models.CharField(max_length=2)
    upag = models.CharField(max_length=50)
    matricula_instituidor = models.CharField(max_length=50, blank=True, null=True)
    situacao_funcional = models.CharField(max_length=50)
    rjur = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nome

class MatriculaDebitos(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='matriculas')
    matricula = models.CharField(max_length=50, null=True, blank=True)
    debito = models.CharField(max_length=50, null=True, blank=True)
    banco = models.CharField(max_length=100, null=True, blank=True)
    orgao = models.CharField(max_length=100, null=True, blank=True)
    pmt = models.FloatField(null=True, blank=True)
    prazo = models.IntegerField(null=True, blank=True)
    tipo_contrato = models.CharField(max_length=50, null=True, blank=True)
    contrato = models.CharField(max_length=50, null=True, blank=True)
    creditos = models.FloatField(null=True, blank=True)
    debitos = models.FloatField(null=True, blank=True)
    liquido = models.FloatField(null=True, blank=True)
    exc_soma = models.FloatField(null=True, blank=True)
    margem = models.FloatField(null=True, blank=True)
    base_calc = models.FloatField(null=True, blank=True)
    bruta_5 = models.FloatField(null=True, blank=True)
    utilz_5 = models.FloatField(null=True, blank=True)
    saldo_5 = models.FloatField(null=True, blank=True)
    beneficio_bruta_5 = models.FloatField(null=True, blank=True)
    beneficio_utilizado_5 = models.FloatField(null=True, blank=True)
    beneficio_saldo_5 = models.FloatField(null=True, blank=True)
    bruta_35 = models.FloatField(null=True, blank=True)
    utilz_35 = models.FloatField(null=True, blank=True)
    saldo_35 = models.FloatField(null=True, blank=True)
    bruta_70 = models.FloatField(null=True, blank=True)
    utilz_70 = models.FloatField(null=True, blank=True)
    saldo_70 = models.FloatField(null=True, blank=True)
    arq_upag = models.CharField(max_length=50, null=True, blank=True)
    exc_qtd = models.IntegerField(null=True, blank=True)
    
    class Meta:
        unique_together = ('cliente', 'matricula', 'debito')
    
    def __str__(self):
        return f"{self.cliente} - {self.matricula} - {self.debito}"
