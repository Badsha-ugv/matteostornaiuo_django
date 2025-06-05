from rest_framework import serializers, status
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from datetime import datetime, timedelta


from users.serializers import SkillSerializer, JobRoleSerializer, UniformSerializer
from users.models import Skill

from django.contrib.auth import get_user_model

from .models import (
    CompanyProfile,
    JobTemplate,
    Job,
    Vacancy,
    JobApplication,
    Checkin,
    Checkout,
    JobAds,
    FavouriteStaff,
    MyStaff,
    CompanyReview,
)
from users.models import (
    JobRole,
    Skill,
    Uniform,
)

from dashboard.models import Notification

from users.serializers import UserSerializer

from staff.serializers import StaffSerializer
from staff.models import Staff

User = get_user_model()


# done
class CompanyProfileSerializer(serializers.ModelSerializer):
    user_data = serializers.JSONField(write_only=True, required=False, allow_null=True)
    avg_rating = serializers.SerializerMethodField(read_only=True, required=False)

    class Meta:
        model = CompanyProfile
        # fields = '__all__'
        exclude = ["created_at", "updated_at"]
        read_only_fields = ["user"]

    # to_representation method for user
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["user"] = UserSerializer(instance.user).data
        return data

    def get_avg_rating(self, obj):
        reviews = CompanyReview.objects.filter(review_for=obj).aggregate(Avg("rating"))[
            "rating__avg"
        ]
        if reviews:
            return reviews
        else:
            return 0

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user_data", None)
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        return super().update(instance, validated_data)


class JobTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTemplate
        fields = "__all__"
        # read_only_fields = ['profile']


class VacancySerializer(serializers.ModelSerializer):
    application_status = serializers.SerializerMethodField(read_only=True)
    job_name = serializers.SerializerMethodField(read_only=True)
    compoany_image = serializers.SerializerMethodField(read_only=True)
    applicants = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = "__all__"

    def get_job_name(self, obj):
        return obj.job.title
    
    def get_compoany_image(self, obj):
        # get company profile image with query optimization
        company = obj.job.company
        if company.company_logo:
            return company.company_logo.url
        return None

    def get_application_status(self, obj):
        # Use prefetched applications if available
        job_apps = getattr(obj, "_prefetched_jobapplications", None)
        if job_apps is None:
            job_apps = obj.jobapplication_set.all()

        status_counts = {}
        for app in job_apps:
            status_counts[app.job_status] = status_counts.get(app.job_status, 0) + 1

        # Default all possible statuses
        default = {"pending": 0, "accepted": 0, "rejected": 0, "expired": 0}
        default.update(status_counts)
        return default


    def get_applicants(self, obj):
        job_apps = getattr(obj, "_prefetched_jobapplications", None)
        if job_apps is None:
            job_apps = obj.jobapplication_set.select_related("applicant__user")

        return [
            {
                "id": app.applicant.id,
                "first_name": app.applicant.user.first_name,
                "last_name": app.applicant.user.last_name,
                "avatar": app.applicant.avatar.url if app.applicant.avatar else None,
            }
            for app in job_apps
        ]


class CreateVacancySerializers(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    job_title = serializers.PrimaryKeyRelatedField(queryset=JobRole.objects.all())
    skills = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), many=True, required=False
    )
    uniform = serializers.PrimaryKeyRelatedField(
        queryset=Uniform.objects.all(), required=False, allow_null=True
    )
    invited_staff = serializers.ListField(required=False, allow_null=True)

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "job",
            "job_title",
            "number_of_staff",
            "skills",
            "uniform",
            "open_date",
            "close_date",
            "start_time",
            "end_time",
            "location",
            "job_status",
            "invited_staff",
        ]

    def create(self, validated_data):
        skills = validated_data.pop("skills", [])
        invited_staff_id = validated_data.pop("invited_staff", [])

        # print('validated data', validated_data['job'].status)
        vacancy = Vacancy.objects.create(**validated_data)

        vacancy.skills.set(skills)
        # send notifications to the invited staff
        for staff in invited_staff_id:
            # send notifications to the invited staff
            staff = Staff.objects.filter(id=staff).first()
            if staff:
                Notification.objects.create(
                    user=staff.user,
                    message=f"You are invited to {vacancy.job.title} at {vacancy.open_date}. go to the job description.",
                )
        return vacancy


class JobSerializer(serializers.ModelSerializer):
    vacancy_data = serializers.ListField(write_only=True)
    vacancies = VacancySerializer(read_only=True, many=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "company",
            "title",
            "description",
            "status",
            "save_template",
            "vacancies",
            "vacancy_data",
        ]
        read_only_fields = ["company"]
        depth = 1

    def create(self, validated_data):
        user = self.context["request"].user
        vacancy_data = validated_data.pop("vacancy_data", [])
        save_in_template = validated_data.get("save_template")

        if not user.is_client:
            return serializers.ValidationError("Only clients can update jobs.")
        client = CompanyProfile.objects.filter(user=user).first()
        validated_data["company"] = client

        job = Job.objects.create(**validated_data)

        for vacancy in vacancy_data:
            start_date = vacancy.get("open_date")
            end_date = vacancy.get("close_date")

            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            if start_date and end_date:
                current_date = start_date
                while current_date <= end_date:
                    vacancy_copy = vacancy.copy()
                    vacancy_copy["open_date"] = current_date
                    vacancy_copy["close_date"] = current_date
                    vacancy_copy["job"] = job.id
                    vacancy_copy["job_status"] = (
                        "draft" if job.status == False else "active"
                    )
                    # print('vacancy copy', vacancy_copy)
                    vacancy_serializer = CreateVacancySerializers(data=vacancy_copy)
                    if vacancy_serializer.is_valid():
                        vacancy_serializer.save()
                    else:
                        return Response(
                            vacancy_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    # print('current', current_date)
                    current_date = current_date + timedelta(days=1)

            else:
                vacancy["job"] = job.id
                vacancy_serializer = CreateVacancySerializers(data=vacancy)
                if vacancy_serializer.is_valid():
                    vacancy_serializer.save()
                else:
                    return Response(
                        vacancy_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

        if save_in_template:
            JobTemplate.objects.create(
                client=user.profiles,
                job=job,
                name=job.title,
                title=job.title,
                description=job.description,
            )

        return job

    def update(self, instance, validated_data):
        user_ = self.context["request"].user
        vacancy_data = validated_data.pop("vacancy_data", [])
        save_in_template = validated_data.get("save_template", False)

        if not user_.is_client:
            raise serializers.ValidationError("Only clients can update jobs.")
        client = CompanyProfile.objects.filter(user=user_).first()
        validated_data["company"] = client

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if vacancy_data:
            for vacancy_item in vacancy_data:
                vacancy_id = vacancy_item.get("id", None)
                if vacancy_id is not None:
                    vacancy_obj = Vacancy.objects.filter(id=vacancy_id).first()

                    if not vacancy_obj:
                        vacancy_id = None
                    if instance.status:
                        vacancy_item["job_status"] = "active"
                    else:
                        vacancy_item["job_status"] = "draft"
                    # update vacancy using vacancy serializer
                    vacancy_serializer = CreateVacancySerializers(
                        instance=vacancy_obj, data=vacancy_item, partial=True
                    )
                    if vacancy_serializer.is_valid():
                        vacancy_serializer.save()
                    else:
                        # raise error
                        raise serializers.ValidationError(vacancy_serializer.errors)
                else:
                    # create new vacancy
                    vacancy_item["job"] = instance.id

                    if instance.status:
                        vacancy_item["job_status"] = "active"
                    else:
                        vacancy_item["job_status"] = "draft"

                    vacancy_serializer = CreateVacancySerializers(data=vacancy_item)
                    if vacancy_serializer.is_valid():
                        vacancy_serializer.save()
                    else:
                        # raise error
                        raise serializers.ValidationError(vacancy_serializer.errors)

        # if save_in_template:
        #     job_template, created = JobTemplate.objects.get_or_create(client=user_.profiles, job=instance)
        #     if created:
        #         job_template.user = user_
        #         job_template.job = instance
        #         job_template.save()
        if save_in_template:
            job_template, created = JobTemplate.objects.get_or_create(
                client=user_.profiles,
                job=instance,
                name=instance.title,
                title=instance.title,
                description=instance.description,
            )
            if created:
                job_template.name = instance.title
                job_template.title = instance.title
                job_template.description = instance.description
                job_template.save()

        return instance


class JobViewSerializers(serializers.ModelSerializer):
    company = CompanyProfileSerializer(read_only=True)

    class Meta:
        model = Job
        exclude = ("vacancy",)


class JobApplicationSerializer(serializers.ModelSerializer):
    # def __init__(self, *args, **kwargs):
    #     fields = kwargs.pop('fields', None)  # Get dynamic fields if provided
    #     super().__init__(*args, **kwargs)

    #     if fields:
    #         allowed = set(fields)
    #         existing = set(self.fields.keys())
    #         for field_name in existing - allowed:
    #             self.fields.pop(field_name)
    class Meta:
        model = JobApplication
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["vacancy"] = VacancySerializer(instance.vacancy).data
        data["applicant"] = StaffSerializer(instance.applicant).data
        return data


class CheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkin
        exclude = ("created_at",)
        read_only_fields = ["staff"]
        depth = 1


class CheckOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkout
        exclude = ("created_at",)
        read_only_fields = ["staff"]
        depth = 1


class PermanentJobsSerializer(serializers.ModelSerializer):
    skills = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), many=True, write_only=True
    )
    company = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = JobAds
        fields = "__all__"
        read_only_fields = ["company"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["skills"] = SkillSerializer(instance.skills, many=True).data
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        if not user.is_client:
            return None
        skills = validated_data.pop("skills", {})

        client = CompanyProfile.objects.filter(user=user).first()
        validated_data["company"] = client

        job_ads = JobAds.objects.create(**validated_data)
        job_ads.skills.set(skills)
        return job_ads

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if not user.is_client:
            return None

        # Get the CompanyProfile for the user
        client = CompanyProfile.objects.filter(user=user).first()
        validated_data["company"] = client

        # Extract skills from validated_data
        skills = validated_data.pop("skills", None)

        # Get the instance of JobAds
        jobads = JobAds.objects.get(pk=instance.pk)
        if jobads:
            for attr, value in validated_data.items():
                setattr(jobads, attr, value)

            # Update skills if provided
            if skills is not None:
                jobads.skills.set(skills)

            # Save the updated instance
            jobads.save()

            return jobads

        return None


class FavouriteStaffSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField(read_only=True)
    staff = StaffSerializer(read_only=True)

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)  # Get dynamic fields if provided
        super().__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = FavouriteStaff
        fields = ["staff", "company"]


class MyStaffSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)
    client = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = MyStaff
        fields = "__all__"


class JobTemplateSserializers(serializers.ModelSerializer):
    name = serializers.StringRelatedField(read_only=True)
    # client = CompanyProfileSerializer(read_only=True)
    job = JobSerializer(read_only=True)

    class Meta:
        model = JobTemplate
        fields = ["id", "name", "job"]


class CompanyReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyReview
        fields = "__all__"
        depth = 1
