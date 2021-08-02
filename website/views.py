from django.shortcuts import render


def blogpost(request):
    return render(request, 'website/blogpost.html', {})


def dashboard(request):
    return render(request, 'website/dashboard.html', {})


def team(request):
    return render(request, 'website/team.html', {})


def details(request):
    return render(request, 'website/details.html', {})
