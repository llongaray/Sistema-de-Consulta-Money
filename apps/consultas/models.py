from django.db import models

class Cliente(models.Model):
    nome_cliente = models.CharField(max_length=100, blank=False, null=False, default="")
    cpf_cliente = models.CharField(max_length=14, blank=False, null=False, default="")
    uf_cliente = models.CharField(max_length=2, default="")
    cidade_cliente = models.CharField(max_length=100, blank=True, default="")
    telefone_cliente = models.CharField(max_length=20, blank=True, default="")
    idade_cliente = models.IntegerField(blank=True, null=True, default="")

    def __str__(self):
        return self.nome_cliente

class Debito(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default="")
    matricula_cliente = models.CharField(max_length=20, blank=False, null=False, default="")
    upag_cliente = models.CharField(max_length=20, blank=False, null=False, default="")
    banco_cliente = models.CharField(max_length=100, blank=False, null=False, default="")
    cod_orgao_cliente = models.CharField(max_length=20, blank=False, null=False, default="")
    desc_cod_orgao_cliente = models.CharField(max_length=120, blank=False, null=False, default="")
    valor_cliente = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default="")
    margem_cliente = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default="")
    margem_cartao_cliente = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default="")
    prazo_cliente = models.IntegerField(blank=False, null=False, default="")
    situacao_cliente = models.CharField(max_length=100, blank=False, null=False, default="")
    data_cadastro = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['cliente', 'valor_cliente', 'prazo_cliente']

    def __str__(self):
        return f"Débito de {self.cliente.nome_cliente}"
