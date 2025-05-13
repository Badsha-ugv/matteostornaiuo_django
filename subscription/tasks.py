from celery import shared_task
from django.utils import timezone

from client.models import InviteMystaff, CompanyProfile
from utility.utils import send_staff_invitation


@shared_task
def send_staff_joining_mail_task(staff_lists, clinet_id):
    company = CompanyProfile.objects.get(id=clinet_id)
    for staff in staff_lists:
        InviteMystaff.objects.create(
            client=company,
            staff_name=staff['staff_name'],
            staff_email=staff['staff_email'],
            phone=staff['phone'],
            job_role=staff['job_role'],
            employee_type=staff['employee_type'],
            invitation_code = generate_random_invitation_code(company.company_name),
            code_expiry = timezone.now() + timezone.timedelta(days=7),
            is_joined = False
        )
        # send invitation email to staff
        send_staff_invitation(staff['staff_name'], staff['staff_email'], company.company_name)

# generate random invitation 6 digit code
def generate_random_invitation_code(company_name='Unknown'):
    import uuid
    code = f'{company_name}-{str(uuid.uuid4())[:6]}'
    return code


