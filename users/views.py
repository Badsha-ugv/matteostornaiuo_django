from .models import User, StaffInvitation
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from jwt.exceptions import InvalidTokenError

from rest_framework.permissions import AllowAny
from .serializers import (
    StaffSignupSerializer,
    ClientSignupSerializer,
    StaffInvitationSerializer,
    SkillSerializer,
    JobRoleSerializer,
    UniformSerializer
)
from .models import (
    Skill, 
    JobRole,
    Uniform
)
from .email_service import send_staff_signup_email, send_client_signup_email, send_staff_invitation_email_from_client


# Create your views here.
class StaffSignupAPIView(APIView):

    permission_classes = []

    def post(self, request):
        # invited_user = StaffInvitation.objects.all()
        # print("Invited user", invited_user) 
        password = request.POST.get("password", None)
        confirm_password = request.POST.get("confirm_password", None)
        if password == confirm_password:
            serializer = StaffSignupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(is_staff=True)

            staff_member = User.objects.get(email=serializer.data["email"])

            send_staff_signup_email(staff_member.email)
            refresh = RefreshToken.for_user(staff_member)
            tokens = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            data = {
                "user_type": "staff",
                "user": serializer.data,
                "tokens": tokens,
            }
            # serializer.data

            response = status.HTTP_201_CREATED
        else:
            data = ""
            raise ValidationError(
                {"password_mismatch": "Password fields didn not match."}
            )

        return Response(data, status=response)


class ClientSignupAPIView(APIView):

    permission_classes = []

    def post(self, request):
        password = request.POST.get("password", None)
        confirm_password = request.POST.get("confirm_password", None)
        if password == confirm_password:
            serializer = ClientSignupSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(is_staff=True)
            else:
                response = {
                    # "status": status.HTTP_400_BAD_REQUEST,
                    # "success": False,
                    "errors": serializer.errors,
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            staff_member = User.objects.get(email=serializer.data["email"])
            try:
                send_client_signup_email(staff_member)
            except Exception as e:
                pass 
            
            refresh = RefreshToken.for_user(staff_member)
            tokens = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            data = {
                "user_type": "client",
                "user": serializer.data,
                "tokens": tokens,
            }
            response = status.HTTP_201_CREATED
        else:
            data = ""
            raise ValidationError(
                {"password_mismatch": "Password fields didn not match."}
            )

        return Response(data, status=response)


# for invite staff from clinets
class StaffInvitationList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        staffInvitation = StaffInvitation.objects.filter(user=request.user)
        serializer = StaffInvitationSerializer(staffInvitation, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "List of staff invitations",
            "data": serializer.data
        }
        return Response(response_data)

    def post(self, request, format=None):
        serializer = StaffInvitationSerializer(data=request.data)
        # print("DFS", request.data['invitations'][0]['staff_email'])
        if serializer.is_valid():
            for invocation in request.data['invitations']:
                staff_email = invocation['staff_email']
                # message = f" {staff_email} {invocation['job_role']} "
                # send_staff_invitation_email_from_client(staff_email, message)

            serializer.save(user=request.user)
            # serializer.save()

            response_data = {
                "message": "Staff invitations sent successfully.",
                "status": 200,
                "success": True,
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# skill api


class SkillList(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "List of skills",
            "data": serializer.data
        }
        return Response(response_data)


class JobRoleList(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        job_roles = JobRole.objects.all()
        serializer = JobRoleSerializer(job_roles, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "List of job roles",
            "data": serializer.data
        }
        return Response(response_data)


class UniformList(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        uniforms = Uniform.objects.all()
        serializer = UniformSerializer(uniforms, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "List of uniforms",
            "data": serializer.data
        }
        return Response(response_data)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({
                    "success": False,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Authorization header with Bearer token required.",
                    "errors": {"error": ["Access token is required."]}
                }, status=status.HTTP_400_BAD_REQUEST)

            access_token_str = auth_header.split(' ')[1]
            access_token = AccessToken(access_token_str)

            # Manually blacklist the token using OutstandingToken
            token_obj = OutstandingToken.objects.filter(token=access_token_str).first()
            if token_obj:
                BlacklistedToken.objects.get_or_create(token=token_obj)

            return Response({
                "success": True,
                "status": status.HTTP_200_OK,
                "message": "Successfully logged out.",
            }, status=status.HTTP_200_OK)

        except InvalidTokenError as e:
            return Response({
                "success": False,
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid or expired token.",
                "errors": {"error": [str(e)]}
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "success": False,
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "An error occurred during logout.",
                "errors": {"error": [str(e)]}
            }, status=status.HTTP_400_BAD_REQUEST)