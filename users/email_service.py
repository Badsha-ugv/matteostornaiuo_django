from django.core.mail import send_mail
from django.conf import settings


def send_staff_signup_email(email):
    subject = "Welcome to Our Team!"
    message = "Hello, \n\nThank you for staff signing up as a staff member. We're excited to have you on board!"
    from_email = settings.EMAIL_HOST_USER  # You can configure this in your settings.py

    send_mail(subject, message, from_email, [email])


def send_client_signup_email(email):
    subject = "Welcome to Our Team!"
    message = "Hello, \n\nThank you for client signing up as a staff member. We're excited to have you on board!"
    from_email = settings.EMAIL_HOST_USER  # You can configure this in your settings.py

    send_mail(subject, message, from_email, [email])




def send_staff_invitation_email_from_client(email, message):
    subject = "Welcome to Our Team!"
    # message = "Hello, \n\nThank you for client signing up as a staff member. We're excited to have you on board!"
    # from_email = settings.EMAIL_HOST_USER  # You can configure this in your settings.py
    from_email = settings.EMAIL_HOST_USER  # You can configure this in your settings.py

    send_mail(subject, message, from_email, [email])
