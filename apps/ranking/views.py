from django.shortcuts import render
from django.http import JsonResponse
from .forms import ConsultorForm
import json

# Create your views here.
def import_consultores(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        forms_data = json.loads(request.POST.get('forms'))
        valid = True
        for form_data in forms_data:
            form = ConsultorForm(form_data)
            if not form.is_valid():
                valid = False
                break
        if valid:
            for form_data in forms_data:
                form = ConsultorForm(form_data)
                form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Dados inválidos'})
    return render(request, 'ranking/import_consultores.html')