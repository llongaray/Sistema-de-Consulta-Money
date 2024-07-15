from django.shortcuts import render

# Create your views here.
def consultas(request):
    return render(request,'consultas/index.html')