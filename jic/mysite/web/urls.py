
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Inicio, name='Inicio'),
    path('jic/', views.Jic, name='Jic'),
    path('participar/', views.Participar, name='Participar'),
    path('proyectos/', views.Proyectos, name='Proyectos'),
    path('resultados/', views.Resultados, name='Resultados'),
    path('recursos/', views.Recursos, name='Recursos'),
    path('contacto/', views.Contacto, name='Contacto'),
]