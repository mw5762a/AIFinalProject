from django.urls import path
from . import views

urlpatterns = [
    path('', views.journal_form_view, name='home'),  
    path('analyze/', views.journal_form_view, name='analyze'),  
]
