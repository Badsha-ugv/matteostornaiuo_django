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

def calculate_distance(lat1, lon1, lat2, lon2, radius=25):
    # Create tuples for coordinates
    coord1 = (lat1, lon1)
    coord2 = (lat2, lon2)
    
    # Calculate distance using geodesic function
    distance = geodesic(coord1, coord2).meters
    return distance



# send staff joinint envitation mail - html page
def send_staff_invitation(staff_name, staff_email, company_name, company_website=None):
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

