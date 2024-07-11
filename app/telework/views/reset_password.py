
from django.shortcuts import render


def reset_password (request):
    
    return render(request, 'reset_password.html')
    
    