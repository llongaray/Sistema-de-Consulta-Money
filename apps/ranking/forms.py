from django import forms
from .models import Consultor

class ConsultorForm(forms.ModelForm):
    class Meta:
        model = Consultor
        fields = ['nome', 'setor', 'ramal', 'campanha']
