from django.db import models

class Consultor(models.Model):
    nome = models.CharField(max_length=100)
    setor = models.CharField(max_length=100)
    ramal = models.CharField(max_length=20)
    campanha = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
