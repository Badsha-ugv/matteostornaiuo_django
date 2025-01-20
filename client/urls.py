from django.urls import path
from . import views

urlpatterns = [
    path('company/profile/', views.CompanyProfileCreateView.as_view(), name='company_profile'),
    path('company/profile/<int:pk>/', views.CompanyProfileCreateView.as_view()),
    path('company/vacancy/', views.VacancyView.as_view(), name='company_vacancy'),
    path('company/vacancy/<int:pk>/', views.VacancyView.as_view()),
    path('company/jobs/', views.JobView.as_view()),
    path('company/jobs/<int:pk>/', views.JobDetailView.as_view()),
    path('company/jobs/applications/', views.JobApplicationAPI.as_view()),
    path('company/jobs/applications/<int:pk>/', views.JobApplicationAPI.as_view()),

    path('company/jobs/applications/<int:application_id>/add/', views.AcceptApplicantView.as_view()),
    path('company/jobs/vacancy/<int:vacancy_id>/checkin/', views.CheckInView.as_view()),
    path('company/jobs/vacancy/<int:vacancy_id>/checkout/', views.CheckOutView.as_view()),

    path('company/jobs/vacancy/<int:vacancy_id>/checkin/approve/', views.ApproveCheckinView.as_view()),
    path('company/jobs/vacancy/<int:vacancy_id>/checkout/approve/', views.ApproveCheckoutView.as_view()),
    
    

]