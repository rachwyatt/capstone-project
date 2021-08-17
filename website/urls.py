from django.urls import path

from . import views

urlpatterns = [
    path('blogpost', views.blogpost, name='blogpost'),
    path('', views.dashboard, name='dashboard'),
    path('team', views.team, name='team'),
    path('details', views.details, name='details'),
]