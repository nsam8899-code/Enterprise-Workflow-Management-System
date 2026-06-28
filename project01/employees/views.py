from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import HttpResponse

def access_denied(request):
    return render(request, 'employees/access_denied.html')

def dashboard(request):
    # Temporary placeholder for tests, will be replaced with real dashboard later
    return HttpResponse("Welcome to dashboard")
