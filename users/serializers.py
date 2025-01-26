from rest_framework import fields, serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password

from .models import User, Skill, Uniform, JobRole, StaffInvitation, Invitation
import uuid
from .email_service import send_staff_invitation_email_from_client
from django.utils.timezone import now, timedelta
from client.models import MyStaff, CompanyProfile


def code_genator():
    # Generate a UUID
    random_uuid = uuid.uuid4()
    code = str(random_uuid)[-6:]
    return code


# output: 06ac13


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

        invitations_obj = Invitation.objects.filter(staff_email=validated_data["email"]).first()
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
        # add invited users to my staff list 
        
        if invitations_obj:
            # if not invitations_obj.invitation_code == validated_data['invitation_code'] 
            invitations_obj.invitation_code = None
            invitations_obj.save()

        #     invited_by = invitations_obj.staff_invitation.user
        #     client = CompanyProfile.objects.get(user=invited_by)
        #     MyStaff.objects.create(user=user, client=client, status=True)
        #     # send email to invited staff 
        # return user
    # def save(self, *args, **kwargs):
    #     invited_user = StaffInvitation.objects.all()
    #     print("inv users data: ", invited_user)
    #     return super().save(*args, **kwargs)


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
            "invitation_code",
        ]
        read_only_fields = ["staff_invitation"]

    # to represantion for job role
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["job_role"] = JobRoleSerializer(instance.job_role).data
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
            invitation_data["invitation_code"] = code_genator()
            invitation_data["code_expiry"] = now() + timedelta(minutes=1)
            Invitation.objects.create(
                staff_invitation=staff_invitation, **invitation_data
            )

            # send_staff_invitation_email_from_client(invitation_data['staff_email'], f"{invitation_data['staff_email']} {invitation_data['invitation_code']}")
        return staff_invitation
