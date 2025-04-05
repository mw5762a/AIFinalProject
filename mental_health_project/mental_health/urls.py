from django.urls import path
from . import views

#sends to correct place when buttons are pressed and all that jazz 
urlpatterns = [
    path('', views.journal_form_view, name='home'),  
    path('analyze/', views.journal_form_view, name='analyze'),  
    path('download-pdf/', views.download_pdf, name='download_pdf'),  
]
