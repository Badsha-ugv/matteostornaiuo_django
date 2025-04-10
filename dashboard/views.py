from django.shortcuts import render, get_object_or_404
from datetime import date 
from datetime import datetime 
from django.db.models import Q , Count , Prefetch
from django.utils.timesince import timesince
from django.utils.timezone import now


from rest_framework import status, generics 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

# Create your views here.
from .models import  Notification, Report, FAQ, TermsAndConditions
from . serializers import (
    NotificationSerializer, 
    SkillSerializer,
    TermsAndConditionsSerializer,
    ReportSerializer

)

from client.models import CompanyProfile, Vacancy, Job, JobTemplate, JobApplication, FavouriteStaff
from client.serializers import VacancySerializer, JobTemplateSserializers, JobApplicationSerializer
from staff.models import Staff
from users.models import Skill



class NotificationView(APIView):
    def get(self, request):
        user = request.user
        
        notifications = Notification.objects.filter(user=user).order_by('-created_at')
        
        serializer = NotificationSerializer(notifications, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "data": serializer.data,
        }
        return Response(response_data , status=status.HTTP_200_OK)
    

class SkillView(APIView):
    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "data": serializer.data,
        }
        return Response(response_data , status=status.HTTP_200_OK)
    def post(self, request):
        data = request.data 
        # check this name is already exists 
        skill = Skill.objects.filter(name=data['name']).first()
        if skill:
            return Response({"message": "Skill already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SkillSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class FeedJobView(APIView):
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            user = request.user

            vacancy = Vacancy.objects.filter(pk=pk).select_related('job', 'job_title', 'uniform').prefetch_related('skills', 'participants').first()
                
            if not vacancy:
                response = {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "message": "No Vacancy Found",
                    "data": []
                }
                return Response(response, status=status.HTTP_200_OK)
            
            if vacancy.job.company.user == user:
                # serializer = VacancySerializer(vacancy)
                data = {
                    "id": vacancy.id,
                    "company_avatar": vacancy.job.company.company_logo.url if vacancy.job.company.company_logo else None,
                    "job_status": vacancy.job_status,
                    "open_date": vacancy.open_date,
                    "close_date": vacancy.close_date,
                    "start_time": vacancy.start_time,
                    "end_time": vacancy.end_time,
                    "location": vacancy.location,
                    "salary": vacancy.salary,
                    "number_of_staff": vacancy.number_of_staff,
                    "participants": [
                        {
                            "staff_name": staff.user.first_name + " " + staff.user.last_name,
                            "staff_id" : staff.id,
                            "staff_profile": staff.avatar.url if staff.avatar else None,
                            "age": staff.age,
                            "gender": staff.gender,
                            "timesince": f"{timesince(staff.created_at, now())} ago",
                            "job_title": staff.role.name,
                            "is_favourite": True if FavouriteStaff.objects.filter(company=vacancy.job.company, staff=staff).select_related('staff','company').exists() else False,
                        }
                        for staff in vacancy.participants.all()
                    ]
                }
                response = {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "data": data,
                }
                return Response(response, status=status.HTTP_200_OK)
            
        
        user = request.user
        if user.is_client:
            client = CompanyProfile.objects.filter(user=user).first()
            if not client:
                return Response({"error": "Client profile not found."}, status=status.HTTP_404_NOT_FOUND)
            
            job_status = request.query_params.get('status', None)
            open_date = request.query_params.get('open_date', None)
            close_date = request.query_params.get('close_date', None)
            
            start_time = request.query_params.get('start_time', None)
            end_time = request.query_params.get('end_time', None)
            
            search = request.query_params.get('search', None)
            location = request.query_params.get('location', None)
            
            vacancies = Vacancy.objects.filter(job__company=client).select_related(
                'job', 'job_title', 'uniform'
            ).prefetch_related(
                'skills', 'participants'
            ).order_by('-created_at')

            if search:
                vacancies = vacancies.filter(
                    Q(job__title__icontains=search) |
                    Q(skills__name__icontains=search) |
                    Q(job_title__name__icontains=search)
                ).distinct()

            if job_status:
                vacancies = vacancies.filter(job_status=job_status)

            if location:
                vacancies = vacancies.filter(location=location).order_by('-created_at')

            if open_date or close_date:
                try:
                    open_date = datetime.strptime(open_date, '%Y-%m-%d').date()
                    close_date = datetime.strptime(close_date, '%Y-%m-%d').date()
                    vacancies = vacancies.filter(Q(open_date=open_date) | Q(close_date=close_date)).order_by('-created_at')
                except ValueError:
                    return Response(
                        {"error": "Invalid open_date format, expected YYYY-MM-DD."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            if start_time or end_time:
                try:
                    start_time = datetime.strptime(start_time, '%H:%M:%S').time()
                    end_time = datetime.strptime(end_time, '%H:%M:%S').time()
                    vacancies = vacancies.filter(Q(start_time=start_time) | Q(end_time=end_time)).order_by('-created_at')
                except ValueError:
                    return Response(
                        {"error": "Invalid time format, expected HH:MM."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            if not vacancies.exists():
                response = {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "message": "Vacancy Not Found",
                    "data": []
                }
                return Response(
                    response,
                    status=status.HTTP_200_OK
                )
            
            # Prefetch related JobApplications and annotate counts
            vacancies = vacancies.prefetch_related(
                Prefetch('jobapplication_set', queryset=JobApplication.objects.only('applicant__avatar'))
            ).annotate(
                pending_applications=Count('jobapplication', filter=Q(jobapplication__job_status='pending')),
                accepted_applications=Count('jobapplication', filter=Q(jobapplication__job_status='accepted')),
                rejected_applications=Count('jobapplication', filter=Q(jobapplication__job_status='rejected')),
                expired_applications=Count('jobapplication', filter=Q(jobapplication__job_status='expired'))
            ).order_by('-created_at')

            paginator = PageNumberPagination()
            paginator.page_size = 5
            paginated_vacancies = paginator.paginate_queryset(vacancies, request)
            
            job_list = []
            for vacancy in paginated_vacancies:
                
                data = {
                    "id": vacancy.id,
                    "job_status": vacancy.job_status,
                    "job_title": vacancy.job.title,
                    "job_id": vacancy.job.id,
                    "job_role_id": vacancy.job_title.id,
                    "uniform_id": vacancy.uniform.id if vacancy.uniform else None,
                    "skill_ids": [skl.id for skl in vacancy.skills.all()],
                    "company_logo": vacancy.job.company.company_logo.url if vacancy.job.company.company_logo else None,
                    "number_of_staff": vacancy.number_of_staff,
                    "start_date": vacancy.open_date,
                    "start_time": vacancy.start_time,
                    "end_time": vacancy.end_time,
                    "location": vacancy.location,
                    
                    "applicant": [
                        {
                            "id": app.applicant.id,
                            "first_name": app.applicant.user.first_name,
                            "last_name": app.applicant.user.last_name,
                            "avatar": app.applicant.avatar.url if app.applicant.avatar else None
                            
                        } 
                        for app in vacancy.jobapplication_set.all()
                    ],
                    
                    "application_status": {
                        "pending": vacancy.pending_applications,
                        "accepted": vacancy.accepted_applications,
                        "rejected": vacancy.rejected_applications,
                        "expired": vacancy.expired_applications
                    },
                }
                job_list.append(data)

            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "total_objects": paginator.page.paginator.count,
                "total_pages": paginator.page.paginator.num_pages,
                "current_page": paginator.page.number,
                "data": job_list,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        vacancies = Vacancy.objects.filter(job_status='active').select_related('job', 'job_title', 'uniform').prefetch_related('skills', 'participants').order_by('-created_at')
        serializer = VacancySerializer(vacancies, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
class JobCountAPI(APIView):
    def get(self, request):
        user = request.user
        if user.is_client:
            client = CompanyProfile.objects.filter(user=user).first()
            if not client:
                return Response({"error": "Client profile not found."}, status=status.HTTP_404_NOT_FOUND)
            
            vacancies = Vacancy.objects.filter(job__company=client).select_related('job', 'job_title', 'uniform').prefetch_related('skills', 'participants')
            status_count = {
                "active": vacancies.filter(job_status='active').count(),
                "progress": vacancies.filter(job_status='progress').count(),
                "draft": vacancies.filter(job_status='draft').count(),
                "cancelled": vacancies.filter(job_status='cancelled').count(),
                "finished": vacancies.filter(job_status='finished').count(),
            }
            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "data": status_count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

class GetJobTemplateAPIView(APIView):
    def get(self, request, pk=None):
        user = request.user 
        if user.is_client:
            client = CompanyProfile.objects.filter(user=user).first()
            if pk:
                job_template = JobTemplate.objects.filter(client=client, pk=pk).first()
                if job_template:
                    serializer = JobTemplateSserializers(job_template)
                    response_data = {
                        "status": status.HTTP_200_OK,
                        "success": True,
                        "data": serializer.data,
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Job template not found"}, status=status.HTTP_204_NO_CONTENT)
            templates = JobTemplate.objects.filter(client=client)
            # serializer = JobTemplateSserializers(job_template, many=True)
            if not templates.exists():
                return Response({"message": "No job template found"}, status=status.HTTP_204_NO_CONTENT)
            
            template_list = []
            for template in templates:
                data = {
                    "id": template.id,
                    "name": template.name,
                    "title": template.title,
                    "description": template.description,
                    "job_id": template.job.id
                }
                template_list.append(data)

            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "data": template_list,
            }
            return Response(response_data , status=status.HTTP_200_OK)
        return Response({"message": "You are not authorized to access this resource"}, status=status.HTTP_403_FORBIDDEN)
    
    def put(self, request, pk):
        user = request.user
        template = JobTemplate.objects.filter(pk=pk).first()

        data = request.data 
        if user.is_client:
            client = CompanyProfile.objects.filter(user=user).first()
            if template.client == client:
                template.title = data['title'] if data['title'] else template.job.title 
                template.name = data['name'] if data['name'] else template.job.title 
                template.description = data['description'] if data['description'] else template.job.description 
                template.save()

                response = {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "message": "Job templated updated successfully"
                }
                return Response(response, status=status.HTTP_200_OK)
        response = {
            "status": status.HTTP_304_NOT_MODIFIED,
            "success": False,
            "message": "Job template not updated"
        }
        return Response(response)



    def delete(self, request, pk):
        user = request.user 
        if user.is_client:
            client = CompanyProfile.objects.filter(user=user).first()
            job_template = JobTemplate.objects.filter(client=client, id=pk).first()
            if not job_template:
                response = {
                    "status": status.HTTP_200_OK,
                    "success": False,
                    "message": "Job template not found"
                }
                return Response(response, status=status.HTTP_200_OK)
            job_template.delete()
            response = {
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "Job Template Delete Successfully"
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response({"message": "You are not authorized to access this resource"}, status=status.HTTP_403_FORBIDDEN)

class ReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        reports = Report.objects.filter(user=user)
        serializers = ReportSerializer(reports, many=True)
        response = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "List of Report",
            "data": serializers.data
        }
        return Response(response, status=status.HTTP_200_OK)
    
    def post(self, request):
        data= request.data
        # data['user'] = request.user.id
        serializer = ReportSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)

            response = {
                "status": status.HTTP_201_CREATED,
                "success": True,
                "message": "Report sent successfullly",
            }
        else:
            return Response(serializer.errors)
        return Response(response, status=status.HTTP_201_CREATED)




class FAQAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        faqs = FAQ.objects.all()
        data = []
        for faq in faqs:
            obj = {
                "question": faq.question,
                "answer": faq.answer
            }
            data.append(obj)
        response = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "List of Faqs",
            "data": data
        }
        return Response(response, status=status.HTTP_200_OK)
    
class TermsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        terms = TermsAndConditions.objects.all()
        serializers = TermsAndConditionsSerializer(terms, many=True)

        response = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "List of Terms and Conditions",
            "data": serializers.data
        }
        return Response(response, status=status.HTTP_200_OK)