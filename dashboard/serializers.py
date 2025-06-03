from rest_framework import serializers

from .models import Notification, TermsAndConditions, Report, LetmeReview
from staff.serializers import StaffSerializer
from client.models import Vacancy
from client.serializers import JobViewSerializers, VacancySerializer
from users.models import Skill
from django.utils.timesince import timesince


class NotificationSerializer(serializers.ModelSerializer):
    timesince = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = "__all__"
        extra_fields = ['timesince']
    
    def get_timesince(self, obj):
        return timesince(obj.created_at)


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class VacancyJobSerializer(serializers.Serializer):
    job = JobViewSerializers()
    vacancy = VacancySerializer()
    

class TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditions
        exclude = ('created_at',)
    

class ReportSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Report
        fields = '__all__'


class LetmeReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LetmeReview
        fields = '__all__'
        