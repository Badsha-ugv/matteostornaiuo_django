from django.urls import path 
from . import views 


urlpatterns = [
    path('packages/', views.PackageView.as_view()),
    path('webhook/', views.webhook),
    


]