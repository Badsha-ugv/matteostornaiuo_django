from django.urls import path 
from . import views 

urlpatterns = [
    path('dashboard/notification/', views.NotificationView.as_view()),
    path('dashboard/notification/<int:pk>/', views.NotificationView.as_view()),
    path('dashboard/skills/', views.SkillView.as_view()),

    path('dashboard/jobs/', views.FeedJobView.as_view()),
    path('dashboard/jobs/<int:pk>/', views.FeedJobView.as_view()),
    path('dashboard/jobs/status-count/', views.JobCountAPI.as_view()),

    path('job/templates/', views.GetJobTemplateAPIView.as_view()),
    path('job/templates/<int:pk>/', views.GetJobTemplateAPIView.as_view()),

    path('faq/', views.FAQAPIView.as_view()),
    path('terms/', views.TermsAPIView.as_view()),
    path('report/', views.ReportAPIView.as_view()),
    path('letme-review/', views.LetMeReviewAPIView.as_view()),

    
]