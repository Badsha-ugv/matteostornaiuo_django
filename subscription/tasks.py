from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.html import strip_tags
from django.conf import settings

from client.models import InviteMystaff, CompanyProfile



@shared_task
def send_staff_joining_mail_task(staff_count, clinet_id):
    print('i am calling send staff joining mail task')
    company = CompanyProfile.objects.get(id=clinet_id)
    # get last created staff of this company
    staff_lists = InviteMystaff.objects.filter(client=company).order_by('-created_at')[:staff_count]
    print('staff lists', staff_lists)
    if staff_lists.count() == 0:
        print('no staff to send')
        return
    for staff in staff_lists:
        try:
            staff.status = 'active'
            staff.save()
            # send invitation email to staff
            
            # send_staff_invitation(staff['staff_name'], staff['staff_email'], company.company_name)
            send_staff_invitation_task.delay(staff.staff_name, staff.staff_email, company.company_name)
            print('staff invitation mail sent')
        except Exception as e:
            # print(e)
            pass 

    # for staff in staff_lists:
    #     try:
    #         InviteMystaff.objects.create(
    #             client=company,
    #             staff_name=staff['staff_name'],
    #             staff_email=staff['staff_email'],
    #             phone=staff['phone'],
    #             job_role=staff['job_role'],
    #             employee_type=staff['employee_type'],
    #             invitation_code = generate_random_invitation_code(company.company_name),
    #             code_expiry = timezone.now() + timezone.timedelta(days=7),
    #             is_joined = False
    #         )
    #         # send invitation email to staff
    #         send_staff_invitation(staff['staff_name'], staff['staff_email'], company.company_name)
    #     except Exception as e:
    #         # print(e)
    #         pass

# generate random invitation 6 digit code

@shared_task
def send_staff_invitation_task(staff_name, staff_email, company_name, company_website=None):
    print('receiving mail task', staff_name, staff_email, company_name)
    try:
        html_content = render_to_string(
            'staff_invitation.html', {
            'staff_name': staff_name,
            'staff_email': staff_email,
            'company_name': company_name,
            'company_website': company_website if company_website else 'https://www.example.com',
        })
        # # Convert HTML to PDF
        # pdf_file = HTML(string=html_content).write_pdf()

        # # Define storage path
        # pdf_filename = f"staff_invitation.pdf"
        # pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)

        # # Save PDF in Django storage
        # default_storage.save(pdf_filename, ContentFile(pdf_file))

        # Send email
        send_mail(
            subject='Invitation to join ' + company_name + 'as a staff',
            message=strip_tags(html_content),  # Plain text version
            from_email= settings.EMAIL_HOST_USER,
            recipient_list=[staff_email],
            html_message=html_content,  # HTML version
        )
        print('mail sent')
    except Exception as e:
        print('mail is not sent',e)
