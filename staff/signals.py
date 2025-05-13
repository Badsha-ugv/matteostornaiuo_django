from django.db.models.signals import post_save
from django.dispatch import receiver 
from .models import Staff
from users.models import Invitation
from client.models import MyStaff, CompanyProfile, InviteMystaff


@receiver(post_save, sender=Staff)
def add_staff_to_mystaff(sender, instance, created, **kwargs):
    if created:
        # invitation = Invitation.objects.filter(staff_email=instance.user.email).first()
        invitation = InviteMystaff.objects.filter(staff_email=instance.user.email).first()
        if invitation:
            instance.is_letme_staff = False
            instance.save()
            # user = CompanyProfile.objects.filter(user=invited_by).first()
            try:
                client = CompanyProfile.objects.get(user=invitation.client)
                MyStaff.objects.create(staff=instance, client=client, status=True)
            except CompanyProfile.DoesNotExist:
                pass
            
            # send email to invited staff
