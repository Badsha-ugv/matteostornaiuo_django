from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from django.utils import timezone
from django.core.validators import ValidationError
from dateutil.relativedelta import relativedelta
from users.models import JobRole, Skill

from project.s3bucket import CustomS3Storage


User = get_user_model()

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(JobRole, on_delete=models.SET_NULL, null=True)
    nid_number = models.IntegerField(default=0)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=300, blank=True)
    dob = models.DateField(blank=True)
    age = models.IntegerField(null=True, blank=True)
    # avatar = models.ImageField(blank=True, null=True, upload_to='images/staff/avatar/')
    avatar = models.ImageField(blank=True, null=True, storage=CustomS3Storage(), upload_to="staff/avatar/")
    about = models.TextField(blank=True)
    gender = models.CharField(max_length=5, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    post_code = models.CharField(max_length=20, blank=True, null=True)
    cv = models.FileField(blank=True, null=True, storage=CustomS3Storage(), upload_to='staff/cv/')
    video_cv = models.FileField(blank=True, null=True, storage=CustomS3Storage(), upload_to='staff/video_resume/')

    # role = models.ManyToManyField(JobRole, blank=True, related_name='staff_roles')
    skills = models.ManyToManyField(Skill, blank=True, related_name="staff_skill")
    experience = models.ManyToManyField("Experience", blank=True, related_name="staff_experience")
    # review = 
    is_available = models.BooleanField(default=True)
    is_letme_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Staff'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} '
    # calculate age in year
    def age_in_year(self):
        today = datetime.now()
        self.age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return self.age
    
    def save(self, *args, **kwargs):
        self.age_in_year()
        super().save(*args, **kwargs)


class BankDetails(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name='bank_details')
    card_holder_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    swift_code = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True, null=True)
    post_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'{self.staff.user.first_name} {self.staff.user.last_name} Bank Details'
    class Meta:
        verbose_name_plural = 'Bank Details'
        ordering = ['staff']
    


class Experience (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experiences')
    job_role = models.ForeignKey(JobRole, models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    present = models.BooleanField(default=False)
    duration = models.CharField(max_length=50, blank=True, null=True)
    class Meta:
        verbose_name_plural = 'Experience'
        ordering = ['-start_date']
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - {self.job_role} {self.duration} '
    # calculate experience duration
    def calcuate_duration(self):
        if self.present:
            today = timezone.now().date()
            duration = relativedelta(today, self.start_date)
        else:
            duration = relativedelta(self.end_date, self.start_date)
        year = duration.years
        print(year)
        months = duration.months
        if year > 0:
            if months > 0:
                return  f'{year} year {months} month(s)'
            else:
                return  f'{year} year'
        else:
            return  f'{months} month(s)'

    def save(self, *args, **kwargs):
        # if self.end_date and self.end_date < self.start_date:
        #     raise ValidationError("End date should not be earlier than start date")
        if self.present:
            self.end_date = timezone.now().date()
        self.duration =self.calcuate_duration()
        super().save(*args, **kwargs)


class StaffReview(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    vacancy = models.OneToOneField("client.Vacancy", on_delete=models.SET_NULL, null=True)
    job_role = models.CharField(max_length=100, blank=True, null=True)
    review_by = models.ForeignKey("client.CompanyProfile", on_delete=models.SET_NULL,blank=True, null=True)
    rating = models.PositiveIntegerField(validators=[ MaxValueValidator(5)])
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.rating} Star rating on {self.vacancy}'
    class Meta:
        verbose_name_plural = 'Staff Reviews'
        ordering = ['-created_at']

        # add a constrains for check rating max value
        constraints= [
            models.CheckConstraint(
                check=models.Q(rating__gte=1, rating__lte=5),
                name="rating_check"
            )
            
        ]
    # set job role from vacancy.job_title.name in save method
    def save(self, *args, **kwargs):
        if self.vacancy:
            self.job_role = self.vacancy.job_title.name
            self.review_by = self.vacancy.job.company
        super().save(*args, **kwargs)

    
