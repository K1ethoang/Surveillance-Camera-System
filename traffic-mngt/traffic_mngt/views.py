from django.shortcuts import render
from templates import *


def home_view(request):
    return render(request, 'home.html')
