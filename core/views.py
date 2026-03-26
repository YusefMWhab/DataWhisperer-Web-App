from django.template import loader
from django.shortcuts import render, redirect
from django.http import HttpResponse


def dashboard(request):
    
    template = loader.get_template('dashboard.html')

    context = {
        
    }
    return HttpResponse(template.render(context, request))


def documentation_view(request):

    template = loader.get_template('documentation.html')

    context = {
        
    }
    return HttpResponse(template.render(context, request))