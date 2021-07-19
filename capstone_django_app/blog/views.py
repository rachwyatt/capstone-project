from django.shortcuts import render


def blogpost(request):
    return render(request, 'blog/blogpost.html', {})


def dashboard(request):
    return render(request, 'blog/dashboard.html', {})


def team(request):
    return render(request, 'blog/team.html', {})


def details(request):
    return render(request, 'blog/details.html', {})
