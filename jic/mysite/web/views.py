from django.shortcuts import render

def Inicio(request):
    
    return render(request, '_base.html')
