from django.urls import path
from . import views

urlpatterns = [
    # company profile
    path('company/profile/', views.CompanyProfileCreateView.as_view(), name='company_profile'), # read, create
    path('company/profile/image/', views.ClientProfileImageView.as_view()), # update client profile image
    # path('company/profile/<int:pk>/', views.CompanyProfileCreateView.as_view()), # put, delete
    # vacancy

    path('company/vacancy/', views.VacancyView.as_view(), name='company_vacancy'),
    path('company/<int:job_id>/vacancy/', views.VacancyView.as_view()), #post
    path('company/vacancy/<int:pk>/', views.VacancyView.as_view()), # put, delete
    # jobs

    path('company/jobs/', views.JobView.as_view()), 
    path('company/jobs/<int:pk>/', views.JobView.as_view()),
    # favourite staff 

    path('company/staff/favourites/', views.FavouriteStaffView.as_view()),
    path('company/staff/favourites/<int:pk>/', views.FavouriteStaffView.as_view()),
    # my staff

    path('company/staff/own/', views.MyStaffView.as_view()),
    path('company/staff/own/<int:pk>/', views.MyStaffView.as_view()),
    
    # application list in job detail view

    path('company/job/applications/', views.JobApplicationAPI.as_view()),
    path('company/job/applications/<int:pk>/', views.JobApplicationAPI.as_view()), # application details / approve application 
    
    # application list in pending action view

    path('company/job/<int:vacancy_id>/applications/', views.JobApplicationAPI.as_view()),
    path('company/job/<int:vacancy_id>/applications/<int:pk>/', views.JobApplicationAPI.as_view()),

    # job checkin 
    path('company/job/applications/checkin/', views.CheckInView.as_view()),
    # path('company/job/vacancy/applications/checkin/<int:vacancy_id>/', views.CheckInView.as_view()),
    path('company/job/applications/checkin/<int:pk>/', views.CheckInView.as_view()),
    
    # job checkout
    path('company/job/applications/checkout/', views.CheckOutView.as_view()),
    path('company/job/applications/checkout/<int:pk>/', views.CheckOutView.as_view()),

    # company review 
    path('company/review/', views.CompanyReviewView.as_view()),
    path('company/<int:application_id>/review/', views.CompanyReviewView.as_view()), # give review

    # report 


    # give tips 
    path('vacancy/<int:application_id>/tips/', views.TipView.as_view()),




    # job ads
    path('company/job/ads/', views.JobAdsView.as_view()),
    path('company/job/ads/<int:pk>/', views.JobAdsView.as_view()),
    # shifting
    path('company/shifting/<int:shifting_id>/request/', views.ShiftCheckinAcceptView.as_view()),
    path('company/shifting/<int:shifting_id>/accept/<int:pk>/', views.ShiftCheckinAcceptView.as_view()),



    # invitation
    path('company/staff/invited/', views.MyStaffInvitatinView.as_view()),
    path('company/staff/invited/<int:package_id>/', views.MyStaffInvitatinView.as_view()),



]