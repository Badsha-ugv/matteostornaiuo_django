from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from project.s3bucket import     CustomS3Storage
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    phone_number = models.CharField(_("phone number"), max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    is_client = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        # return firstname lastname if available
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name} {self.email}"
        else:
            return self.email


class Skill(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class JobRole(models.Model):
    name = models.CharField(max_length=200)
    staff_price = models.IntegerField(default=0)
    client_price = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "Job Roles"
        ordering = ["name"]

    # if the exactly this name exists raise error
    def save(self, *args, **kwargs):
        # user can udpate the staff_price
        if self.name:
            if JobRole.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
                raise ValidationError("Job role with this name already exists.")
        super().save(*args, **kwargs)



class Uniform(models.Model):
    job_role = models.ForeignKey(
        JobRole, related_name="uniforms", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="images/uniforms/", max_length=255, storage=CustomS3Storage(), blank=True, null=True)
    def __str__(self):
        return f'{self.job_role} - {self.name}'

    class Meta:
        verbose_name_plural = "Uniforms"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if self.name and Uniform.objects.filter(name__iexact=self.name).exists():
            raise ValidationError("Uniform with this name already exists.")
        super().save(*args, **kwargs)


# for invite staff from clinets
class StaffInvitation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} invitation"


class Invitation(models.Model):
    staff_invitation = models.ForeignKey(
        StaffInvitation, related_name="invitations", on_delete=models.CASCADE
    )
    staff_name = models.CharField(max_length=200)
    staff_email = models.EmailField()
    phone = models.CharField(max_length=20)
    job_role = models.ForeignKey(
        JobRole, related_name="invitations_job_role", on_delete=models.SET_NULL, null=True
    )  # cleint can select multipal roles
    employee_type = models.CharField(max_length=200)
    invitation_code = models.CharField(max_length=8, null=True)
    code_expiry = models.DateTimeField(blank=True, null=True)
    # status = models.BooleanField(default=False)

    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff_name} - {self.staff_email}"
