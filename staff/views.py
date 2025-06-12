from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import datetime
from django.db.models import Avg, Count

import csv
from io import StringIO


from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import (
    Staff,
    Experience,
    BankDetails,
    StaffReview

)
from .serializers import (
    StaffSerializer,
    CreateStaffSerializer,
    BankAccountSerializer,
    ExperienceSerializer,
    StaffReviewSerializer


)
from shifting.models import Shifting, DailyShift
from shifting.serializers import ShiftingSerializer, DailyShiftSerializer
from dashboard.models import Notification

from client.models import Job, JobApplication, Vacancy, MyStaff, Checkin, Checkout, JobRole, JobReport, CompanyProfile, FavouriteStaff
from client.serializers import JobApplicationSerializer, CheckinSerializer, CheckOutSerializer

from shifting.models import Shifting, DailyShift
from shifting.serializers import ShiftingSerializer, DailyShiftSerializer

class StaffProfileView(APIView):
    def get(self, request,pk=None, *args, **kwargs):
        user = request.user

        if pk:
            
            try:
                staff = Staff.objects.get(id=pk)
            except Staff.DoesNotExist:
                return Response({
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Staff not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            segments = request.path.strip('/').split('/')
            if 'app' in segments:
                serializer = StaffSerializer(staff)
                response_data = {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "message": "Staff profile retrieved successfully",
                    "data": serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            
            
            StaffReview.objects.filter(staff=staff).values('job_role').annotate(avg_rating=Avg('rating'), review_count=Count('id') )
            user = request.user
            if user.is_client:
                client = CompanyProfile.objects.filter(user=request.user).first()
            
            # custom response data
            staff_data = {
                "id": staff.id,
                "image": staff.avatar.url if staff.avatar else None,
                "name": staff.user.first_name + " " + staff.user.last_name,
                "role": staff.role.name,
                "contact": staff.phone,
                "email": staff.user.email,
                "age": staff.age,
                "gender": staff.gender,
                "cv": staff.cv.url if staff.cv else None,
                "video_cv": staff.video_cv.url if staff.video_cv else None,
                "rating": [
                    {
                        "job_role": review.job_role,
                        "avg_rating": review.avg_rating,
                        "review_count": review.review_count
                    } for review in StaffReview.objects.filter(staff=staff).annotate(avg_rating=Avg('rating'), review_count=Count('id') )
                ],
                "job_info":{
                    "total_apply": staff.job_applications.count(),

                    "total_approved": staff.job_applications.filter(is_approve=True, job_status='accepted').count(),

                    "total_cancel": staff.job_applications.filter(is_approve=False, job_status='cancelled').count(),

                    "total_late": staff.job_applications.filter(is_approve=False, job_status='late').count(),
                },
                "is_favaurite": True if user.is_client and  FavouriteStaff.objects.filter(company=client, staff=staff).select_related('staff','company').exists() else False


            }


            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "Staff profile retrieved successfully",
                "data": staff_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        try:
            staff = Staff.objects.get(user=user)
        except Staff.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Staff profile not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        
        serializer = StaffSerializer(staff)
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "Staff profile retrieved successfully",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
        
    def post(self, request, *args, **kwargs):
        serializer = CreateStaffSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            staff = serializer.save()
            # show staff serializers in response
            res = StaffSerializer(staff)
            response = {
                "status": status.HTTP_201_CREATED,
                "message": "Staff profile created successfully",
                "data": res.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        data = request.data
        user = request.user
        staff = Staff.objects.filter(user=user).first()
        if staff:
            serializer = CreateStaffSerializer(staff, data=data, partial=True)
            if serializer.is_valid():
                data = serializer.save()
                res = StaffSerializer(data)
                response = {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "message": "Staff profile updated successfully",
                    "data": res.data
                }
                return Response(response, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Staff profile not found"
        }, status=status.HTTP_404_NOT_FOUND)


class JobApplicationView(APIView):
    def get(self, request, pk=None, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            return Response ({
                "status": status.HTTP_403_FORBIDDEN,
                "message": "Only staff can access this endpoint"
            })
        try:
            staff = Staff.objects.filter(user=user).first()
        except Staff.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Staff not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        applications = JobApplication.objects.filter(applicant=staff)
        if not applications:
            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "No job applications found"
            }
            return Response(response_data, status=status.HTTP_200_OK)
        serializer = JobApplicationSerializer(applications, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "Job applications retrieved successfully",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request,pk=None, *args, **kwargs):
        user = request.user 
        if user.is_staff:
            staff = Staff.objects.filter(user=user).first()
            # check vacancy exists  and not expired or closed
            try:
                vacancy = Vacancy.objects.get(id=pk)
                if JobApplication.objects.filter(applicant=staff, vacancy=vacancy).exists():
                    response_data = {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "success": False,
                        "message": "You have already submitted a job application for this vacancy"
                    }
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
                
                # check if application expired
                if vacancy.close_date < timezone.now().date():
                    response_data = {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "success": False,
                        "message": "This vacancy has expired"
                    }
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
                
                # # check if vacancy is closed
                # if vacancy.is_closed:
                #     response_data = {
                #         "status": status.HTTP_400_BAD_REQUEST,
                #         "success": False,
                #         "message": "This vacancy is closed"
                #     }
                #     return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
                
                # check if vacancy is already filled
                # if vacancy.is_full:
                #     response_data = {
                #         "status": status.HTTP_400_BAD_REQUEST,
                #         "success": False,
                #         "message": "This vacancy is already filled"
                #     }
                #     return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            except Vacancy.DoesNotExist:
                response_data = {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "success": False,
                    "message": "Vacancy Not Found"
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            application = JobApplication.objects.create(
                applicant = staff,
                vacancy=vacancy
            )
            # send notification to client
            notification = Notification.objects.create(
                user=vacancy.job.company.user,
                message=f'{staff} has submitted a job application for {vacancy.job_title}'
            )
            
            response_data = {
                "status": status.HTTP_201_CREATED,
                "success": True,
                "message": "Job application created successfully",
                # "data": JobApplicationSerializer(application).data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        # user must be a staff instance
        response_data = {
            "status": status.HTTP_403_FORBIDDEN,
            "success": False,
            "message": "You are not authorized to create this resource"
        }
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)


class StaffJobView(APIView): # jobapplication 
    def get(self, request, pk=None, *args, **kwargs):
        """UPCOMMING JOB LIST"""
        user = request.user
        try:
            staff = Staff.objects.get(user=user)
        except Staff.DoesNotExist:
            response_data = {
                "status": status.HTTP_403_FORBIDDEN,
                "success": False,
                "message": "You are not authorized to view this resource"
            }
            return Response(response_data, status=status.HTTP_403_FORBIDDEN)
        # UPCOMMING JOB DETAILS VIEW / WITH CHECKIN CHECKOUT REPORT PAGE BUTTON INCLUDED
        if pk:
            try:
                job_application = JobApplication.objects.get(applicant=staff, id=pk)
                
            except JobApplication.DoesNotExist:
                response_data = {
                    "status": status.HTTP_404_NOT_FOUND,
                    "success": False,
                    "message": "Job not found"
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            
            checkin_status = Checkin.objects.filter(application=job_application).first()
            checkout_status = Checkout.objects.filter(application=job_application).first()
            
            # serializer = JobApplicationSerializer(job_application)
            obj = {
                'id': job_application.id,
                'job_title': job_application.vacancy.job.title,
                'shift_price': job_application.vacancy.salary,
                'company_logo': job_application.vacancy.job.company.company_logo.url if job_application.vacancy.job.company.company_logo else None,
                'company_id': job_application.vacancy.job.company.id,
                'job_role': job_application.vacancy.job_title.name,
                'job_description': job_application.vacancy.job.description,
                'uniform': {
                    'name': job_application.vacancy.uniform.name,
                    'description': job_application.vacancy.uniform.description,
                    'image': job_application.vacancy.uniform.image.url if job_application.vacancy.uniform.image else None,
                } if job_application.vacancy.uniform else None,
                'skills': [x for x in job_application.vacancy.skills.all().values_list('name', flat=True)],
                
                'date': job_application.vacancy.open_date,
                'start_time': job_application.vacancy.start_time,
                'end_time': job_application.vacancy.end_time,
                'location': job_application.vacancy.location,
                
                "job_status": job_application.job_status,
                "checkin_approve": job_application.checkin_approve,
                "checkout_approve": job_application.checkout_approve,
                "checkin_status": checkin_status.checkin_status if checkin_status else "Not Checked In",
                "checkout_status": checkout_status.checkout_status if checkout_status else "Not Checked Out"

            }
            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "Job retrieved successfully",
                "data": obj
            }
            return Response(response_data, status=status.HTTP_200_OK)
        # upcomming job list
        job_application = JobApplication.objects.filter(applicant=staff,is_approve=True).select_related('vacancy','applicant')

        
        # application_serializer = JobApplicationSerializer(job_application, many=True)
        applications = []
        for application in job_application:
            checkin_status = Checkin.objects.filter(application=application).first()
            checkout_status = Checkout.objects.filter(application=application).first()
            obj = {
                'id': application.id,
                'job_title': application.vacancy.job.title,
                'shift_price': application.vacancy.salary,
                'company_logo': application.vacancy.job.company.company_logo.url if application.vacancy.job.company.company_logo else None,
                'job_role': application.vacancy.job_title.name,
                'date': application.vacancy.open_date,
                'start_time': application.vacancy.start_time,
                'end_time': application.vacancy.end_time,
                'location': application.vacancy.location,
                "job_status": application.job_status,
                "checkin_approve": application.checkin_approve,
                "checkout_approve": application.checkout_approve,
                "checkin_status": checkin_status.checkin_status if checkin_status else "Not Checked In",
                "checkout_status": checkout_status.checkout_status if checkout_status else "Not Checked Out"
            }
            applications.append(obj)
        
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "List of Upcomming Jobs",
            "data": applications
        }
        return Response(response_data, status=status.HTTP_200_OK)
    def post(self, request,pk, *args, **kwargs):
        """CKECKIN / CHECKIN REQUEST"""
        user = request.user
        data = request.data
        if user.is_staff:
            try:
                staff = Staff.objects.only('id').get(user=user)
            except Staff.DoesNotExist:
                response_data = {
                    "status": status.HTTP_403_FORBIDDEN,
                    "success": False,
                    "message": "You are not authorized to create this resource"
                }
                return Response(response_data, status=status.HTTP_403_FORBIDDEN)
            
            
            try:
                application = JobApplication.objects.get(id=pk, applicant=staff)
            except JobApplication.DoesNotExist:
                response_data = {
                    "status": status.HTTP_404_NOT_FOUND,
                    "success": False,
                    "message": "JobApplication not found"
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

            if application.is_approve:
                if data['type'] == 'checkin':
                    

                    # if already checkedin 
                    if Checkin.objects.filter(application=application).exists():
                        response_data = {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "success": False,
                            "message": "You have already checked in this"
                        }
                        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
                    Checkin.objects.create(
                        application=application,
                        in_time = timezone.now(),
                        location = data['location']
                    )

                    response_data = {
                        "status": status.HTTP_200_OK,
                        "success": True,
                        "message": "Shift checked in successfully",
                        # "data": JobApplicationSerializer(application).data
                    }
                    # send notification to the client 
                    notification = Notification.objects.create(
                        user=application.vacancy.job.company.user,
                        message=f'{staff} has checked in for {application.vacancy.job_title}! Approve the checkin request.'
                    )
                    return Response(response_data, status=status.HTTP_200_OK)
                

                if data['type'] == 'checkout':
                    if not application.checkin_approve is True:
                        response_data = {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "success": False,
                            "message": "You have not checked in this"
                        }
                        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
                    
                    # if already checkedout
                    if Checkout.objects.filter(application=application).exists():
                        response_data = {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "success": False,
                            "message": "You have already checked out this"
                        }
                        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
                    
                    Checkout.objects.create(
                        application=application,
                        out_time = timezone.now(),
                        location = data['location']
                    )
                    
                    response_data = {
                        "status": status.HTTP_200_OK,
                        "success": True,
                        "message": "Shift checked out successfully",
                        # "data": JobApplicationSerializer(application).data
                    }
                    # send notification to the client
                    notification = Notification.objects.create(
                        user=application.vacancy.job.company.user,
                        message=f'{staff} has checked out for {application.vacancy.job_title}! Approve the checkout request.'
                    )
                    return Response(response_data, status=status.HTTP_200_OK)
                
        response_data = {
            "status": status.HTTP_400_BAD_REQUEST,
            "success": False,
            "message": "Invalid request"
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

# VERSION 2
class ShiftRequestView(APIView):
    def get(self, request, pk=None,  *args, **kwargs):
        user = request.user
        staff = Staff.objects.filter(user=user).first()
        
        if pk:
            daily_shift = DailyShift.objects.filter(id=pk, staff=staff).first()
            if daily_shift:
                serializer = DailyShiftSerializer(daily_shift)
                response_data = {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "message": "Shift request retrieved successfully",
                    "data": serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "status": status.HTTP_404_NOT_FOUND,
                    "success": False,
                    "message": "Shift request not found"
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            
        if DailyShift.objects.filter(staff=staff, status=False).exists():
            shifts = DailyShift.objects.filter(staff=staff, status=False)
            serializer = DailyShiftSerializer(shifts, many=True)
            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "Shift requests retrieved successfully",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "status": status.HTTP_404_NOT_FOUND,
                "success": False,
                "message": "No pending shift requests found"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk=None, *args, **kwargs):
        data = request.data 

        
        daily_shift = DailyShift.objects.get(pk=pk)

        if data['type'] == 'request':
            if data['value'] == True:
                daily_shift.status = True
                daily_shift.shift_status = 'accepted'
                daily_shift.save()
                notification = Notification.objects.create(
                    user=daily_shift.shift.company.user,
                    message=f'{daily_shift.staff.user } has accepted your shift request.'
                )
                response_data = {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "message": "Shift request accepted successfully",
                    "data": DailyShiftSerializer(daily_shift).data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            elif data['value'] == False:
                daily_shift.status = False
                daily_shift.shift_status = 'rejected'
                daily_shift.save()
                notification = Notification.objects.create(
                    user=daily_shift.shift.company.user,
                    message=f'{daily_shift.staff.user } has rejected your shift request.'
                )
                response_data = {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "message": "Shift request rejected successfully",
                    "data": DailyShiftSerializer(daily_shift).data
                }
                
                return Response(response_data, status=status.HTTP_200_OK)

class ShiftCheckinView(APIView):
    def get(self,request, pk=None, *args, **kwargs):
        user = request.user
        staff = Staff.objects.filter(user=user).first()

        if pk:
            daily_shift = DailyShift.objects.filter(id=pk, staff=staff, status=True, checkin_status=False).first()
            if daily_shift:
                response = {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "message": "Shift check-in request retrieved successfully",
                    "data": DailyShiftSerializer(daily_shift).data
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "status": status.HTTP_404_NOT_FOUND,
                    "success": False,
                    "message": "Shift check-in request not found"
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
        # return all not checkin shift
        shifts = DailyShift.objects.filter(staff=staff, status=True, checkin_status=False)
        serializer = DailyShiftSerializer(shifts, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "Shift check-in requests retrieved successfully",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request, pk=None, *args, **kwargs):
        data = request.data
        daily_shift = DailyShift.objects.get(pk=pk)
        if data['type'] == 'checkin':
            # daily_shift.checkin_status = True # client approve it 
            daily_shift.checkin_time = timezone.now()
            daily_shift.checkin_location = data['checkin_location']
            daily_shift.save()
            notification = Notification.objects.create(
                user=daily_shift.shift.company.user,
                message=f'{daily_shift.staff.user } has checked-in for your shift.'
            )
            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "Shift check-in request accepted successfully",
                # "data": DailyShiftSerializer(daily_shift).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        response = {
            "status": status.HTTP_400_BAD_REQUEST,
            "success": False,
            "message": "Invalid type. Expected 'checkin' or 'checkout'"
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

class ShiftCheckoutView(APIView):
    def get(self,request, pk=None, *args, **kwargs):
        user = request.user
        staff = Staff.objects.filter(user=user).first()
        if pk:
            daily_shift = DailyShift.objects.filter(id=pk, checkout_status=False).first()
            response = {
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "Shift check-out request retrieved successfully",
                "data": DailyShiftSerializer(daily_shift).data
            }
            return Response(response, status=status.HTTP_200_OK)
        # return all not checkout shift
        shifts = DailyShift.objects.filter(staff=staff, checkout_status=False)
        serializer = DailyShiftSerializer(shifts, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "Shift check-out requests retrieved successfully",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request, pk=None, *args, **kwargs):
        data = request.data
        daily_shift = DailyShift.objects.get(pk=pk)
        if data['type'] == 'checkout':
            # daily_shift.checkout_status = True # client approve it 
            daily_shift.checkout_time = timezone.now()
            daily_shift.checkout_location = data['checkout_location']
            daily_shift.save()
            notification = Notification.objects.create(
                user=daily_shift.shift.company.user,
                message=f'{daily_shift.staff.user } has checked-out for your shift.'
            )
            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "Shift check-out request accepted successfully",
                # "data": DailyShiftSerializer(daily_shift).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        response = {
            "status": status.HTTP_400_BAD_REQUEST,
            "success": False,
            "message": "Invalid type. Expected 'checkin' or 'checkout'"
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    

# client shift 
class StaffShiftView(APIView):
    def get(self, request, pk=None, *args, **kwargs):
        user = request.user
        try:
            staff = Staff.objects.get(user=user)
        except Staff.DoesNotExist:
            response_data = {
                "status": status.HTTP_404_NOT_FOUND,
                "success": False,
                "message": "Staff not found"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
        if staff.is_letme_staff:
            myshift = DailyShift.objects.filter(staff=staff)
            serializer = DailyShiftSerializer(myshift, many=True)
            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "Shift records retrieved successfully",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            try:
                mystaff = MyStaff.objects.get(staff=staff)
            except MyStaff.DoesNotExist:
                response_data = {
                    "status": status.HTTP_404_NOT_FOUND,
                    "success": False,
                    "message": "Your staff record not found"
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            try:
                myshift, created = Shifting.objects.get_or_create(shift_for=mystaff, company=mystaff.client )

                if myshift.shifts.count() > 0:
                    shifts = myshift.dailyshift_set.all()
                else:
                    response_data = {
                        "status": status.HTTP_404_NOT_FOUND,
                        "success": False,
                        "message": "No shift records found"
                    }
                    return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            except Shifting.DoesNotExist:
                response_data = {
                    "status": status.HTTP_404_NOT_FOUND,
                    "success": False,
                    "message": "Your shifting record not found"
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            
            
            # shifts = DailyShift.objects.filter(shift=shifts)
            serializer = DailyShiftSerializer(shifts, many=True)
            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "Shift records retrieved successfully",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

class ExperienceView(APIView):
    def get(self, request, pk=None, *args, **kwargs):
        user = request.user
        
        if pk is not None:
            try:
                experience = Experience.objects.get(id=pk)
                if experience.user == user:
                    serializer = ExperienceSerializer(experience)
                    response_data = {
                        "status": status.HTTP_200_OK,
                        "success": True,
                        "message": "Experience record retrieved successfully",
                        "data": serializer.data
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
            except Experience.DoesNotExist:
                response_data = {
                    "status": status.HTTP_404_NOT_FOUND,
                    "success": False,
                    "message": "Experience record not found"
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        experiences = Experience.objects.filter(user=user)
        serializers = ExperienceSerializer(experiences, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "Experience records retrieved successfully",
            "data": serializers.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ExperienceSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save(user=user)
            # if user have staff then add it in experience list 
            if user.is_staff:
                staff = Staff.objects.filter(user=user).first()
                if staff:
                    staff.experience.add(obj)
            response_data = {
                "status": status.HTTP_201_CREATED,
                "success": True,
                "message": "Experience record created successfully",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffReviewView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user and user.is_staff:
            staff = Staff.objects.filter(user=user).first()
            if staff:
                reviews = StaffReview.objects.filter(staff=staff)
                serializer = StaffReviewSerializer(reviews, many=True)
                response_data = {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "message": "Reviews retrieved successfully",
                    "data": serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            response_data = {
                "status": status.HTTP_404_NOT_FOUND,
                "success": False,
                "message": "Staff not found"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        response_data = {
            "status": status.HTTP_403_FORBIDDEN,
            "success": False,
            "message": "Unauthorized access"
        }
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)
    
    def post(self, request, application_id, *args, **kwargs):
        user = request.user
        data = request.data
        if user and user.is_client:
            application = JobApplication.objects.get(id=application_id)
            if application.vacancy.job.company.user == user:
                if StaffReview.objects.filter(staff=application.applicant, vacancy=application.vacancy).exists():
                    review = StaffReview.objects.get(staff=application.applicant, vacancy=application.vacancy)
                    review.rating = data['rating']
                    review.content = data['content']
                    review.save()
                    response_data = {
                        "status": status.HTTP_200_OK,
                        "success": True,
                        "message": "Review updated successfully",
                        "data": StaffReviewSerializer(review).data
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                review = StaffReview.objects.create(
                    staff=application.applicant,
                    vacancy = application.vacancy,
                    rating = data['rating'],
                    content = data['content']
                )
            else:
                response_data = {
                    "status": status.HTTP_403_FORBIDDEN,
                    "success": False,
                    "message": "Unauthorized access"
                }
                return Response(response_data, status=status.HTTP_403_FORBIDDEN)
            response_data = {
                "status": status.HTTP_201_CREATED,
                "success": True,
                "message": "Review submitted successfully",
                "data": StaffReviewSerializer(review).data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data = {
            "status": status.HTTP_403_FORBIDDEN,
            "success": False,
            "message": "Unauthorized access"
        }
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)
    

class StaffWorkingHoursView(APIView):
    def get(self, request, staff_id, *args, **kwargs):
        staff = Staff.objects.filter(id=staff_id).first()
        if staff:
            working_hours = JobReport.objects.filter(job_application__applicant=staff)
            
            working_hours_list = []
            for report in working_hours:
                obj = {
                    ""
                    "job_title": report.job_application.vacancy.job.title,
                    "company": report.job_application.vacancy.job.company.company_name,
                    "working_hour": report.working_hour,
                    "extra_hour": report.extra_hour,
                    "regular_pay": report.regular_pay,
                    "overtime_pay": report.overtime_pay,
                    "tips": report.tips,
                    "total_pay": report.total_pay,

                    "date": report.job_application.created_at,
                    "shift": f'{report.job_application.vacancy.start_time} to {report.job_application.vacancy.end_time}',
                    "location": report.job_application.vacancy.location
                }
                working_hours_list.append(obj)
                # convert this data into csv file and send it to the response.
                # a downloadable csv file
                # if the request comes from the app url 
                # split the path
                url_route = request.path.split('/')
                if 'app' in url_route:
                    # make csv file, save it in media folder
                    pass 
                
                csv_file = StringIO()
                csv_writer = csv.writer(csv_file)
                headers = ['Job Title', 'Company', 'Working Hour', 'Extra Hour', 'Regular Pay', 'Overtime Pay', 'Tips', 'Total Pay', 'Date', 'Shift', 'Location']
                csv_writer.writerow(headers)
                csv_writer.writerow(obj.values())
                response_data = {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "message": "List of working hours",
                    "data": csv_file.getvalue()
                }
                return Response(response_data, status=status.HTTP_200_OK)

            # response_data = {
            #     "status": status.HTTP_200_OK,
            #     "success": True,
            #     "message": "List of working hours",
            #     "data": working_hours_list
            # }
            # return Response(response_data, status=status.HTTP_200_OK)
        response_data = {
            "status": status.HTTP_404_NOT_FOUND,
            "success": False,
            "message": "Staff not found"
        }
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
    

# staff profile preview
class UpcommingJobsPreview(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk, format=None):
        staff = get_object_or_404(Staff, id=pk)


        upcoming_jobs = JobApplication.objects.filter(applicant=staff, is_approve=True).select_related('vacancy__job__company')
        # use pagination 
        page = request.GET.get('page',1)
        paginator = Paginator(upcoming_jobs, 5)
        try:
            jobs = paginator.page(page)
        except PageNotAnInteger:
            jobs = paginator.page(1)
        except EmptyPage:
            jobs = paginator.page(paginator.num_pages)

        

        # serializer = JobApplicationSerializer(jobs, many=True)
        upcoming_jobs = []
        def get_application_status(obj):
            # return the count of each job status 
            job_application = JobApplication.objects.filter(vacancy=obj)
            pending = job_application.filter(job_status='pending').count()
            accepted = job_application.filter(job_status='accepted').count()
            rejected = job_application.filter(job_status='rejected').count()
            expierd = job_application.filter(job_status='expired').count()
            return {'pending': pending, 'accepted': accepted,'rejected': rejected, 'expired': expierd}
        
        # split route for app
        app_route = request.path.strip('/').split('/')
        if 'app' in app_route:
            for job in jobs:
                obj = {
                    'id': job.id,
                    'job_title': job.vacancy.job.title,
                    'company_logo': job.vacancy.job.company.company_logo.url if job.vacancy.job.company.company_logo else None,
                    # 'job_role': job.vacancy.job_title.name,
                    "job_role": job.vacancy.job_title.name,
                    "job_status": job.vacancy.job_status,
                    "date": job.vacancy.created_at,
                    "start_time": job.vacancy.start_time,
                    "end_time": job.vacancy.end_time,
                    "location": job.vacancy.location,
                }
                upcoming_jobs.append(obj)

            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "Upcoming Jobs",
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "current_page": jobs.number,
                "data": upcoming_jobs
            }
            return Response(response_data, status=status.HTTP_200_OK)


        for job in jobs:
            obj = {
                'id': job.id,
                'job_title': job.vacancy.job.title,
                'company_logo': job.vacancy.job.company.company_logo.url if job.vacancy.job.company.company_logo else None,
                # 'job_role': job.vacancy.job_title.name,
                "job_status": job.vacancy.job_status,
                "date": job.vacancy.created_at,
                "application_status": get_application_status(job.vacancy)
            }
            upcoming_jobs.append(obj)

        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "Upcoming Jobs",
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "current_page": jobs.number,
            "data": upcoming_jobs
        }
        return Response(response_data, status=status.HTTP_200_OK)


# job history- save as upcomming jobs. only status is completed
class JobHistoryPreveiw(APIView):
    permission_classes = [IsAuthenticated]

    # def get_application_status(self,obj):
    #         # return the count of each job status 
    #         job_application = JobApplication.objects.filter(vacancy=obj)
    #         pending = job_application.filter(job_status='pending').count()
    #         accepted = job_application.filter(job_status='accepted').count()
    #         rejected = job_application.filter(job_status='rejected').count()
    #         expierd = job_application.filter(job_status='expired').count()
    #         return {'pending': pending, 'accepted': accepted,'rejected': rejected, 'expired': expierd}
    

    def get(self, request, pk, format=None):
        staff = get_object_or_404(Staff, id=pk)
        
        job_history = JobApplication.objects.filter(applicant=staff, is_approve=True, job_status='completed').select_related('vacancy__job__company')
        # serializer = JobApplicationSerializer(job_history, many=True)
        # add pagination
        page = request.GET.get('page',1)
        paginator = Paginator(job_history, 5)
        try:
            jobs = paginator.page(page)
        except PageNotAnInteger:
            jobs = paginator.page(1)
        except EmptyPage:
            jobs = paginator.page(paginator.num_pages)  
        
        url_route = request.path.strip('/').split('/')
        if 'app' in url_route:
            data = {
                    "total_apply": staff.job_applications.count(),

                    "total_approved": staff.job_applications.filter(is_approve=True, job_status='accepted').count(),

                    "total_cancel": staff.job_applications.filter(is_approve=False, job_status='cancelled').count(),

                    "total_late": staff.job_applications.filter(is_approve=False, job_status='late').count(),
                }
            response_data = {
                "status": status.HTTP_200_OK,
                "success": True,
                "message": "Job History",
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "current_page": jobs.number,
                "data": data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        job_history_list = []
        for job in job_history:
            obj = {
                'id': job.id,
                'job_title': job.vacancy.job.title,
                'company_logo': job.vacancy.job.company.company_logo.url if job.vacancy.job.company.company_logo else None,
                # 'job_role': job.vacancy.job_title.name,
                "job_role": job.vacancy.job_title.name,
                "job_status": job.vacancy.job_status,
                "date": job.vacancy.open_date,
                "start_time": job.vacancy.start_time,
                "end_time": job.vacancy.end_time,
                # get review content for the vacancy
                "locatin":job.vacancy.location,
                "review": StaffReview.objects.filter(staff=staff, vacancy=job.vacancy).values('rating', 'content').first(),

            }
            job_history_list.append(obj)

        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "Job History",
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "current_page": jobs.number,
            "data": job_history_list
        }
        return Response(response_data, status=status.HTTP_200_OK)

# review preview
class ReviewPreview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        staff = get_object_or_404(Staff, id=pk)
        review_queryset = StaffReview.objects.filter(staff=staff)

        page = request.GET.get('page', 1)
        paginator = Paginator(review_queryset, 3)

        try:
            paginated_reviews = paginator.page(page)
        except PageNotAnInteger:
            paginated_reviews = paginator.page(1)
        except EmptyPage:
            paginated_reviews = paginator.page(paginator.num_pages)

        reviews_data = []
        for review in paginated_reviews:
            reviews_data.append({
                "company_image": review.vacancy.job.company.company_logo.url if review.vacancy.job.company.company_logo else None,
                "company_name": review.vacancy.job.company.company_name,
                "job_role": review.job_role,
                "rating": review.rating,
                "content": review.content,
                "date": review.created_at
            })

        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "Reviews",
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "current_page": paginated_reviews.number,
            "data": reviews_data
        }
        return Response(response_data, status=status.HTTP_200_OK)

# cancel job api


class CancelJobAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        vacancy = get_object_or_404(Vacancy, id=pk)
        user = request.user
        if user.is_staff:
            staff = Staff.objects.filter(user=user).only('id').first()
            if staff:
                if staff in vacancy.participants.all():
                    vacancy.participants.remove(staff)
                    job_application = JobApplication.objects.filter(vacancy=vacancy,applicant=staff).first()
                    if job_application:
                        job_application.job_status = 'cancelled'
                        job_application.save()
                        notification = Notification.objects.create(
                            user=staff.user,
                            message=f'{staff} has cancelled the job application for {vacancy.job_title}'
                        )
                        response_data = {
                            "status": status.HTTP_200_OK,
                            "success": True,
                            "message": "Job application cancelled successfully",
                            "data": JobApplicationSerializer(job_application).data
                        }
                        return Response(response_data, status=status.HTTP_200_OK)
                    else:
                        response_data = {
                            "status": status.HTTP_404_NOT_FOUND,
                            "success": False,
                            "message": "Job application not found"
                        }
                        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
                else:
                    response_data = {
                        "status": status.HTTP_403_FORBIDDEN,
                        "success": False,
                        "message": "You are not authorized to cancel this job application"
                    }
                    return Response(response_data,status=status.HTTP_403_FORBIDDEN)
                

class JobReportView(APIView):
    def get(self, request,application_id,pk=None):
        user = request.user
        # get 'past' from query params
        params = request.query_params.get('past', None)
        if user.is_staff:
            staff = Staff.objects.filter(user=user).first()
            try:
                job_application = JobApplication.objects.get(id=application_id)
            except JobApplication.DoesNotExist:
                response_data = {
                    "status": status.HTTP_404_NOT_FOUND,
                    "success": False,
                    "message": "Job Application not found"
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            if params =='' or params == None:
                # get current application report
                job_report = JobReport.objects.filter(job_application=job_application).first()
                if job_report:
                    data = {
                        "id": job_report.id,
                        "full_name": job_report.job_application.applicant.user.first_name + " " + job_report.job_application.applicant.user.last_name,
                        "job_role": job_application.vacancy.job_title.name,
                        "date": job_application.vacancy.open_date,
                        "start_time": job_application.vacancy.start_time,
                        "end_time": job_application.vacancy.end_time,
                        "total_working_hours": job_application.total_working_hours,
                        "base_salary": job_application.vacancy.job_title.staff_price,
                        "regular_pay": job_report.regular_pay,
                        "overtime_pay": job_report.overtime_pay,
                        "tips": job_report.tips,
                        "total_pay": job_report.total_pay,
                        "created_at": job_report.created_at
                    
                    }
                    response = {
                        "status": status.HTTP_200_OK,
                        "success": True,
                        "message": "Job Report retrieved successfully",
                        "data": data
                    }
                    return Response(response, status=status.HTTP_200_OK)
                    
                else:
                    response = {
                        "status": status.HTTP_200_OK,
                        "success": True,
                        "message": "No report found",
                        "data": []
                    }
                    return Response(response, status=status.HTTP_200_OK)
        return Response({
            "status": status.HTTP_403_FORBIDDEN,
            "success": False,
            "message": "Unauthorized access"
        }, status=status.HTTP_403_FORBIDDEN)