from rest_framework import fields, serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password

from .models import User, Skill, Uniform, JobRole, StaffInvitation, Invitation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ("id", "email", "first_name", "last_name", "password")
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_client",
            "is_staff",
            "date_joined",
        )
        extra_kwargs = {"email": {"required": False}}  # Mark email as not required
        # fields = "__all__"


class StaffSignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        if validate_password(validated_data["password"]) == None:
            password = make_password(validated_data["password"])
            user = User.objects.create(
                # username=validated_data["username"],
                email=validated_data["email"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                password=password,
                is_staff=True,
            )
        return user


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class ClientSignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        if validate_password(validated_data["password"]) == None:
            password = make_password(validated_data["password"])
            user = User.objects.create(
                # username=validated_data["username"],
                email=validated_data["email"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                password=password,
                is_client=True,
            )
        return user


class JobRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRole
        fields = ["id", "name", "price_per_hour"]


class UniformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Uniform
        fields = ["id", "name", "description"]


#  invite staff from clients
class InviteSerializer(serializers.ModelSerializer):
    job_role = serializers.PrimaryKeyRelatedField(queryset=JobRole.objects.all())
    class Meta:
        model = Invitation
        # fields = '__all__'
        fields = [
            "staff_invitation",
            "staff_name",
            "staff_email",
            "phone",
            "job_role",
            "employee_type",
        ]
        read_only_fields = ["staff_invitation"]

    # to represantion for job role 
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['job_role'] = JobRoleSerializer(instance.job_role).data
        return data


class StaffInvitationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    invitations = InviteSerializer(many=True)

    class Meta:
        model = StaffInvitation
        fields = ["user", "invitations"]

    def create(self, validated_data):
        invitations_data = validated_data.pop("invitations")
        staff_invitation = StaffInvitation.objects.create(**validated_data)
        for invitation_data in invitations_data:
            Invitation.objects.create(
                staff_invitation=staff_invitation, **invitation_data
            )
        return staff_invitation
