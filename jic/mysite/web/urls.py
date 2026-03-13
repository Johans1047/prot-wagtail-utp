
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Inicio, name='Inicio'),
    path('jic/', views.Jic, name='Jic'),
    path('participar/', views.Participar, name='Participar'),
    path('proyectos/', views.Proyectos, name='Proyectos'),
    path('proyectos/<int:project_id>/', views.ProyectoDetalle, name='ProyectoDetalle'),
    path('jic/coordinadores/', views.JicCoordinadores, name='JicCoordinadores'),
    path('resultados/', views.Resultados, name='Resultados'),
    path('resultados/selecciones/', views.Selecciones, name='Selecciones'),
    path('recursos/', views.Recursos, name='Recursos'),
    path('contacto/', views.Contacto, name='Contacto'),
]