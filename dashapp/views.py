from django.shortcuts import render
from .models import Jd


def blogpost(request):
    return render(request, 'website/blogpost.html', {})


def dashboard(request):
    jobs = Jd.objects.all()
    return render(request, 'website/dashboard.html', {'jobs':jobs})


def team(request):
    return render(request, 'website/team.html', {})


def details(request):
    return render(request, 'website/details.html', {})
