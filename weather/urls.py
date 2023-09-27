from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('clear-cities/', views.clear_cities, name='clear_cities'),  # Add this line
]