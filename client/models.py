from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
from django.utils import timezone
from django.core.validators import ValidationError

from users.models import Skill, Uniform, JobRole
from staff.models import Staff
from project.s3bucket  import CustomS3Storage

User = get_user_model()

class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profiles')
    company_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    company_email = models.EmailField(max_length=50)
    billing_email = models.EmailField(max_length=50)
    company_address = models.CharField(max_length=200)
    tax_number = models.PositiveIntegerField(blank=True, null=True)
    company_details  = models.TextField(blank=True)
    company_logo = models.ImageField(blank=True, null=True, max_length=255 ,storage=CustomS3Storage(), upload_to='images/company/logo/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name = 'Company Profile'
        verbose_name_plural = 'Company Profiles'
        ordering = ['-created_at']

class Job(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # vacancy = models.ManyToManyField(Vacancy, related_name='jobs', blank=True)
    
    status = models.BooleanField(default=True) # is_published
    save_template= models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-created_at']
    # add index to created_at field
    indexes = [
            models.Index(fields=['created_at']),
        ]


JOB_STATUS = (
    ('active', 'Active'),
    ('progress', 'InProgress'),
    ('draft', 'Draft'),
    ('cancelled', 'Cancelled'),
    ('finished', 'Finished'),
)
class Vacancy(models.Model):
    # client = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, blank=True, related_name='vacancies')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="vacancies")
    job_title = models.ForeignKey(JobRole, on_delete=models.SET_NULL, null=True)
    number_of_staff = models.IntegerField(default=1)
    skills = models.ManyToManyField(Skill, related_name='skills', blank=True)  
    uniform = models.ForeignKey(Uniform, on_delete=models.SET_NULL, blank=True, null=True)
    
    open_date = models.DateField()
    close_date = models.DateField(blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    job_status = models.CharField(max_length=255, choices=JOB_STATUS, default='active')
    
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    participants = models.ManyToManyField(Staff, related_name='participants', blank=True)
    shift_job = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.job}  {self.job_title}'
    
    class Meta:
        verbose_name = 'Job Vacancy'
        verbose_name_plural = 'Job Vacancy'
        ordering = ['-created_at']
    
        indexes = [
            models.Index(fields=['open_date', 'close_date', 'start_time', 'end_time']),
        ]

    def calculate_salary(self):
        # calculate hour form start and end time
        hours = (self.end_time.hour - self.start_time.hour) + (self.end_time.minute - self.start_time.minute) / 60
        self.salary = (self.job_title.staff_price * hours * self.number_of_staff) 
        return self.salary
    
    # set salary in save method
    def save(self, *args, **kwargs):
        self.calculate_salary()
        super().save(*args, **kwargs)



    
class JobTemplate(models.Model):
    name = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    client = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    job =   models.ForeignKey(Job, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.job.title
    
    class Meta:
        verbose_name = 'Job Template'
        verbose_name_plural = 'Job-Templates'
    # add name from job title
    # def save(self, *args, **kwargs):
    #     self.name = self.job.title
    #     self.title = self.job.title
    #     self.description = self.job.description 
    #     super().save(*args, **kwargs)

    

# job status 
JOB_STATUS = (
    ('pending', 'PENDING'),
    ('accepted', 'ACCEPTED'),
    ('rejected', 'REJECTED'),
    ('expired', 'EXPIRED'),
    ('late', 'LATE'),
    ('completed', 'COMPLETED')
)
class JobApplication(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    applicant = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='job_applications')
    is_approve = models.BooleanField(default=False)
    in_time = models.DateTimeField(blank=True, null=True)
    out_time = models.DateTimeField(blank=True, null=True)
    checkin_location = models.CharField(max_length=255, blank=True, null=True)
    checkout_location = models.CharField(max_length=255, blank=True, null=True)
    
    job_status = models.CharField(max_length=10, choices=JOB_STATUS, default='pending')
    checkin_approve = models.BooleanField(default=False)
    checkout_approve = models.BooleanField(default=False)
    
    total_working_hours = models.DurationField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # calculate total working hours
    def calculate_total_working_hours(self):
        if self.checkin_approve and self.checkout_approve:
            self.total_working_hours = self.out_time - self.in_time
            return self.total_working_hours

    # set delay in save method
    def save(self, *args, **kwargs):
        self.calculate_total_working_hours()
        super().save(*args, **kwargs)
    def __str__(self):
        return f'{self.applicant.user.email} - {self.vacancy.job_title}'


class StaffInvitation(models.Model):
    """INVITE STAFF TO JOIN THE JOB"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.staff.user.email} -invited in {self.vacancy.job_title}'

class Checkin(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE)
    in_time = models.DateTimeField(blank=True, null=True)
    location =  models.CharField(max_length=255, blank=True, null=True)
    distance = models.IntegerField(default=0, blank=True, null=True, editable=False)
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    # calculate distance from vacancy.location to location
    def calculate_distance(self):
        # calculate distance using google map api
        # use geocoder library for this
        pass

    def __str__(self):
        return f'{self.application.applicant} - checked in at {self.in_time}'

class Checkout(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE)
    out_time = models.DateTimeField(blank=True, null=True)
    location =  models.CharField(max_length=255, blank=True, null=True)
    distance = models.IntegerField(default=0, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.application.applicant} - checked out at {self.out_time}'
    

# job_type like full-time
JOB_TYPE = (
    ('full time', 'full time'),
    ('part time', 'part time'),
    ('contract', 'contract'),
    
)
class JobAds(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.BooleanField(default=False) # set choices field later


    job_type = models.CharField(max_length=20, choices=JOB_TYPE, default='full time')
    number_of_staff = models.IntegerField(default=1)
    skills = models.ManyToManyField(Skill, related_name='permanent_skills', blank=True)
    start_date = models.DateTimeField(db_index=True)
    website_url = models.URLField(blank=True)
    contact_percentage = models.IntegerField(default=0)
    login_email = models.EmailField(max_length=200)
    is_paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.job_title
    
    class Meta:
        verbose_name = 'Permanent Job'
        verbose_name_plural = 'Permanent Jobs'
        ordering = ['-created_at']
        # set indexing on start_date

class JobAdsJoiningRequest(models.Model):
    ads = models.ForeignKey(JobAds, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    joininig_date = models.DateTimeField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.staff.user.email} - requested joining {self.ads.job_title}'
    
class MyStaff(models.Model):
    client = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    # staff = models.ManyToManyField(Staff, related_name='my_staff', blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.staff}'
    
    class Meta:
        verbose_name = 'My Staff'
        verbose_name_plural = 'My Staffs'
        ordering = ['-created_at']

class FavouriteStaff(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, blank=True, on_delete=models.CASCADE,related_name='favourites_staff')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Favourite Staff'
        ordering = ['-created_at']
        # unique_together = (('company', 'staff'),)
    
    def __str__(self):
        return f'{self.company.company_name}'
    

class JobReport(models.Model):
    job_application = models.OneToOneField(JobApplication, on_delete=models.SET_NULL, null=True, related_name='job_report')
    working_hour = models.IntegerField(null=True, blank=True)
    extra_hour = models.IntegerField(null=True, blank=True)
    regular_pay = models.DecimalField(null=True,blank=True, decimal_places=2, max_digits=10)
    overtime_pay = models.DecimalField(null=True,blank=True, decimal_places=2, max_digits=10)
    # tax = models.DecimalField(null=True,  decimal_places=2, max_digits=10, default=25)
    total_pay = models.DecimalField(max_digits=50, decimal_places=2, blank=True, null=True)
    tips = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Job Report - {self.job_application}'

    def generate_report(self):
        if self.job_application.total_working_hours:
            self.working_hour = int(self.job_application.total_working_hours.total_seconds() / 3600)  # Convert timedelta to hours
            base_rate = self.job_application.vacancy.job_title.staff_price  # Get hourly pay rate
            
            # Calculate overtime (if work > 8 hours)
            if self.working_hour > 9:
                self.extra_hour = self.working_hour - 9
            else:
                self.extra_hour = 0
            
            # Regular Pay: First 8 hours at base rate
            self.regular_pay = base_rate * min(self.working_hour, 9)
            
            # Overtime Pay: Extra hours at 1.4x the base rate
            self.overtime_pay = self.extra_hour * base_rate * 1.4
            
            # # Tax (25% of total earnings before tax)
            # total_earnings = self.regular_pay + self.overtime_pay
            # if self.tips > 0:
            #     total_earnings += self.tips  # Add tips to total earnings
            # self.tax = total_earnings * 0.25  # 25% tax
            
            # Final Total Pay after deducting tax
            self.total_pay = self.regular_pay + self.overtime_pay
            
    # create report csv file
    # def generate_report_csv(self):
    #     # create a csv file
    #     csv_file = StringIO()
    #     csv_writer = csv.writer(csv_file)
        
    #     # write headers
    #     headers = ['Job Title', 'Vacancy Title', 'Company', 'Working Hour', 'Extra Hour', 'Regular Pay', 'Overtime Pay', 'Tips', 'Total Pay']
    #     csv_writer.writerow(headers)
        
    #     # write data
    #     data = [
    #         self.job_application.vacancy.job.title,
    #         self.job_application.vacancy.job_title.name,
    #         self.job_application.vacancy.job.company.company_name,
    #         self.working_hour,
    #         self.extra_hour,
    #         self.regular_pay,
    #         self.overtime_pay,
    #         self.tips,
    #         self.total_pay
    #     ]
    #     csv_writer.writerow(data)
        
    #     # return the csv file as a string
    #     return csv_file.getvalue()
    class Meta:
        verbose_name_plural = 'Job Reports'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.generate_report()
        super().save(*args, **kwargs)



class CompanyReview(models.Model):
    review_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    review_for = models.ForeignKey(CompanyProfile, on_delete=models.SET_NULL, null=True)
    application = models.ForeignKey(JobApplication, on_delete=models.SET_NULL, null=True)
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5)])
    content = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.rating} Star rating from {self.review_by}'

    class Meta:
        verbose_name_plural = 'Company Reviews'
        ordering = ['-created_at']


class InviteMystaff(models.Model):
    """INVITE USER TO JOIN THE COMPANY"""
    client = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    staff_name = models.CharField(max_length=200)
    staff_email = models.EmailField()
    phone = models.CharField(max_length=20)
    job_role = models.CharField(max_length=200)
    employee_type = models.CharField(max_length=200)
    invitation_code = models.CharField(max_length=8, null=True)
    code_expiry = models.DateTimeField(blank=True, null=True)
    is_joined = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff_name} - {self.staff_email}"
    
    class Meta:
        verbose_name_plural = 'Invite Staff'
        ordering = ['-created_at']
        unique_together = ('staff_email', 'client')
    
