# calculate distance 
from geopy.distance import geodesic
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from weasyprint import HTML
import os

from client.models import InviteMystaff


def calculate_distance(lat1, lon1, lat2, lon2, radius=25):
    # Create tuples for coordinates
    coord1 = (lat1, lon1)
    coord2 = (lat2, lon2)
    
    # Calculate distance using geodesic function
    distance = geodesic(coord1, coord2).meters
    return distance



# send staff joinint envitation mail - html page
# def send_staff_invitation(staff_name, staff_email, company_name, company_website=None):
#     html_content = render_to_string(
#         'staff_invitation.html', {
#         'staff_name': staff_name,
#         'staff_email': staff_email,
#         'company_name': company_name,
#         'company_website': company_website if company_website else 'https://www.example.com',
#     })
#     # # Convert HTML to PDF
#     # pdf_file = HTML(string=html_content).write_pdf()

#     # # Define storage path
#     # pdf_filename = f"staff_invitation.pdf"
#     # pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)

#     # # Save PDF in Django storage
#     # default_storage.save(pdf_filename, ContentFile(pdf_file))

#     # Send email
#     send_mail(
#         subject='Invitation to join ' + company_name + 'as a staff',
#         message=strip_tags(html_content),  # Plain text version
#         from_email= settings.EMAIL_HOST_USER,
#         recipient_list=[staff_email],
#         html_message=html_content,  # HTML version
#     )

def generate_random_invitation_code(company_name='Unknown'):
    import uuid
    code = f'{company_name}-{str(uuid.uuid4())[:6]}'
    return code


def save_invited_staff(staff_data, client):
    for staff in staff_data:
        try:
            InviteMystaff.objects.create(
                client=client,
                staff_name=staff['staff_name'],
                staff_email=staff['staff_email'],
                phone=staff['phone'],
                job_role=staff['job_role'],
                employee_type=staff['employee_type']
                # invitation_code = generate_random_invitation_code(client.company_name),
                # code_expiry = timezone.now() + timezone.timedelta(days=7),
            )
            # send invitation email to staff
            # send_staff_invitation(staff['staff_name'], staff['staff_email'], company.company_name)
        except Exception as e:
            print(e)
            pass