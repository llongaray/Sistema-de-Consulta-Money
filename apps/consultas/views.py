from django.shortcuts import render

# Create your views here.
def gerencimento(request):
    return render(request, "consultas/index.html")