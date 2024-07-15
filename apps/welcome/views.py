from django.shortcuts import render

# Create your views here.
def welcome(request):
    return render(request,'welcome/welcome.html')

def log(request):
    return render(request,'welcome/log.html')

def cad(request):
    return render(request,'welcome/cad.html')