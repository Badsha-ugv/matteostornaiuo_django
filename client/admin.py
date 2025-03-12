from django.contrib import admin

from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.contrib.filters.admin import RangeDateFilter, RangeDateTimeFilter
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields

from . models import (
    CompanyProfile,
    JobTemplate,
    Job,
    Vacancy,
    JobApplication,
    StaffInvitation,
    Checkout,
    Checkin,
    JobAds,
    MyStaff, FavouriteStaff,
    JobReport,
    CompanyReview



)

@admin.register(CompanyProfile)
class CompanyProfileAdmin(ModelAdmin):
    list_display = ('company_name', 'contact_number', 'company_email','tax_number','company_address', 'created_at')
    search_fields = ('company_name', 'contact_number', 'company_email', 'company_address')
    list_per_page =  20
    list_filter_sheet = False 

class VacancyInline(StackedInline):  # or admin.StackedInline for a different layout
    model = Vacancy  
    extra = 0
    fields = (
        'job_title', 'number_of_staff', 'skills', 'uniform', 'open_date', 'close_date',
        'start_time', 'end_time', 'location', 'job_status', 'salary', 'participants', 'shift_job'
    )
    readonly_fields = ('salary',)
    show_change_link = True

    def get_queryset(self, request):
        # Optimize the queryset to reduce database queries
        return super().get_queryset(request).select_related('job_title', 'uniform').prefetch_related('skills', 'participants')

@admin.register(Job)
class JobAdmin(ModelAdmin):
    list_display = ('title', 'company', 'status', 'created_at')
    list_filter = ('status', 'company')
    search_fields = ('title', 'description', 'company__name')
    ordering = ('-created_at',)
    list_per_page = 20
    list_filter_sheet = False
    inlines = [VacancyInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company')
    

@admin.register(Vacancy)
class VacancyAdmin(ModelAdmin):
    list_display = ('job__title','job_title__name', 'salary', 'job_status', 'open_date','start_time', 'close_date','end_time')
    # list_filter = ('job_title','client__company_name')
    list_editable = ('job_status','open_date','close_date','start_time', 'end_time')
    search_fields = ('job_title__name','job__title')
    ordering = ('-created_at',)
    date_hierarchy = 'open_date'
    list_filter = ('job_status','job_title','created_at','job')
    # list_filter_sheet = False
    list_per_page = 50
    readonly_fields = ('salary',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job','job_title', 'uniform').prefetch_related('skills','participants')



@admin.register(FavouriteStaff)
class FavouriteStaffAdmin(ModelAdmin):
    list_display = ('company','staff', 'created_at' ) 
    list_filter = ('company__company_name',)
    search_fields = ('company__company_name', 'staff__user__first_name', 'staff__user__last_name', 'staff__user__email')
    list_filter_sheet = False 
    list_per_page = 50

@admin.register(JobTemplate)
class JobTemplateAdmin(ModelAdmin):
    pass 




@admin.register(JobApplication)
class JobApplicationAdmin(ModelAdmin):
    list_display = ('vacancy__job__title','applicant','vacancy__job_title','in_time', 'out_time','checkin_approve', 'checkout_approve','total_working_hours', 'applicant__is_letme_staff', 'job_status',  'is_approve', 'created_at')

    list_filter = ('is_approve','checkin_approve', 'checkout_approve', 'job_status', 'created_at')
    search_fields = ('vacancy__job__title','vacancy__job_title__name', 'applicant__user__first_name', 'applicant__user__email')
    list_filter_sheet = True 
    list_per_page = 20
    # list_editable = ('is_approve',)
    
    # fieldset for checkin checout time 
    fieldsets = (
        ('Job Application Details', {
            'fields': (
                'vacancy',
                'applicant',
                'job_status',
                'is_approve',
                
            )
        }),
        ('Check-in/Check-out Details', {
            'fields': (
                'in_time',
                'out_time',
                'checkin_location',
                'checkout_location',
                'checkin_approve', 
                'checkout_approve',
                "total_working_hours"
                
            ),
        })
        )

@admin.register(StaffInvitation)
class StaffInvitationAdmin(ModelAdmin):
    list_display = ('staff', 'vacancy',  'created_at', 'status')

@admin.register(Checkin)
class CheckinAdmin(ModelAdmin):
    list_display = ('staff', 'vacancy', 'in_time', 'is_approved')
@admin.register(Checkout)
class CheckoutAdmin(ModelAdmin):
    list_display = ('staff', 'vacancy', 'out_time', 'status')

@admin.register(JobAds)
class PermanentJobsAdmin(ModelAdmin):
    list_display = ('job_title', 'company', 'start_date', 'number_of_staff', 'is_paid', 'created_at')
    list_filter_sheet = False
    list_filter = ('is_paid', 'company__company_name')
    search_fields = ('job_title', 'company__company_name')
    # horizontal filter by date
    # date_hierarchy = 'start_date'

@admin.register(MyStaff)
class MyStaffAdmin(ModelAdmin):
    list_display = ('client', 'staff', 'start_date', 'status')
    list_filter_sheet = False
    search_fields = ('client__company_name', 'staff__user__first_name', 'staff__user__last_name', 'status')
    list_filter = ('status', 'client__company_name')


# class JobReportResource(resources.ModelResource):
#     applicant_name = fields.Field(column_name='Applicant Name')

#     def dehydrate_applicant_name(self, job_report):
#         return f"{job_report.job_application.applicant.user.first_name} {job_report.job_application.applicant.user.last_name}"

#     vacancy_title = fields.Field(column_name='Vacancy Title', attribute='job_application__vacancy__job_title')
#     working_hour = fields.Field(column_name='Working Hour', attribute='working_hour')
#     extra_hour = fields.Field(column_name='Extra Hour', attribute='extra_hour')
#     regular_pay = fields.Field(column_name='Regular Pay', attribute='regular_pay')
#     overtime_pay = fields.Field(column_name='Overtime Pay', attribute='overtime_pay')
#     total_pay = fields.Field(column_name='Total Pay', attribute='total_pay')

#     class Meta:
#         model = JobReport
#         fields = ('applicant_name', 'vacancy_title', 'working_hour', 'extra_hour', 'regular_pay', 'overtime_pay', 'total_pay')

@admin.register(JobReport)
class JobReportAdmin(ModelAdmin):
    list_display = ['job_application', 'working_hour', 'extra_hour', 'regular_pay', 'overtime_pay', 'tips', 'tax', 'total_pay', 'created_at']
    search_fields = ('job_application__vacancy__job_title__name','job_application__applicant__user__first_name', 'job_application__applicant__user__last_name')
    list_filter_sheet = False
    list_filter = ( 'created_at',)
    list_per_page = 20
    date_hierarchy = 'created_at'



@admin.register(CompanyReview)
class CompanyReviewAdmin(ModelAdmin):
    list_display = ('review_for', 'review_by', 'rating', 'content', 'created_at')
    list_filter = ('review_for__company_name',"rating")
    search_fields = ('review_for__company_name', 'review_by__user__first_name', 'review_by__user__last_name')
    list_filter_sheet = True
    list_per_page = 50
    search_help_text = "Search by company name"
    # list_display_links = None
    def has_add_permission(self, request):
        """Disable the add button."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable the edit button."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable the delete button."""
        return True