from django.urls import path 
from . import views 


urlpatterns = [
    path('packages/', views.PackageView.as_view()),
    path('subscription/packages/<int:pkg_id>/checkout/', views.package_checkout),
    path('webhook/', views.webhook),
    


]