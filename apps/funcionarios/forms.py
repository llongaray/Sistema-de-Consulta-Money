from django import forms
from .models import Ranking

class PhotoUploadForm(forms.ModelForm):
    funcionario = forms.ModelChoiceField(queryset=Ranking.objects.all(), label='Funcionário', required=True)

    class Meta:
        model = Ranking
        fields = ['foto', 'funcionario']
