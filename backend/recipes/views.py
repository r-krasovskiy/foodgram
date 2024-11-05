from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def placeholder_view(request):
    return HttpResponse("Страница в разработке.")
