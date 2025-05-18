import stripe 
from datetime import datetime
import json 

from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import  csrf_exempt
from django.contrib.auth import get_user_model
from django.http import HttpResponse


from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view

from . models import (
    Packages,
    Subscription
)

from.serializers import (
    PackagesSerializer,
    
)

from client.models import CompanyProfile, InviteMystaff
from .tasks import send_staff_joining_mail_task

# Initialize your Stripe API
stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()

class PackageView(APIView):
    def get(self, request):
        packages = Packages.objects.all()
        serializer = PackagesSerializer(packages, many=True)
        response = {
            "status": status.HTTP_200_OK,
            "success": True,
            "message": "List of packages",
            "data": serializer.data
        }
        return Response(response)

# --------------------- WEBHOOK HANDLER ---------------------
@csrf_exempt
def webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        print('Webhook event type:', event.type)
    except Exception as e:
        print('Error deserializing webhook:', e)
        return HttpResponse(status=400)
    
    if event.type == 'customer.subscription.created':
        data = event['data']['object']
        metadata = data.get('metadata', {})
        user_id = metadata.get('user_id')
        package_id = metadata.get('package_id')
        staff_count = int(metadata.get('staff_count'))
        # obj = json.loads(event['data']['object']['metadata']['staff'])
        stripe_subscription_id = data['id']


        try:
            user = User.objects.get(id=user_id)
            client = CompanyProfile.objects.get(user=user)
            package = Packages.objects.get(id=package_id)
            subscription = Subscription.objects.filter(user=user, package=package, stripe_subscriptoin_id=stripe_subscription_id).first()
            if subscription:
                subscription.end_date = datetime.fromtimestamp(data['current_period_end'])
                subscription.status = 'active'
                subscription.save()
            else:    
                Subscription.objects.create(
                    user=user,
                    package=package,
                    stripe_subscriptoin_id=stripe_subscription_id,
                    end_date=datetime.fromtimestamp(data['current_period_end']),
                    status='active',  # Will be updated to active after payment succeeds
                )

            # send staff joining mail
            send_staff_joining_mail_task.delay(staff_count, client.id)
            # bulk create staff invitations
            # for staff in obj:
            #     InviteMystaff.objects.create(
            #         client=client,
            #         staff_name=staff['staff_name'],
            #         staff_email=staff['staff_email'],
            #         phone=staff['phone'],
            #         job_role=staff['job_role'],
            #         employee_type=staff['employee_type']
            #     )
            #     # send invitation email to staff
            #     send_staff_invitation(staff['staff_name'], staff['staff_email'], client.company_name)
        except Exception as e:
            print("Error creating local subscription:", e)
        return HttpResponse(status=200)

    elif event.type == 'customer.subscription.updated':
        data = event['data']['object']
        metadata = data.get('metadata', {})
        user_id = metadata.get('user_id')
        package_id = metadata.get('package_id')
        staff_count = int(metadata.get('staff_count'))
        stripe_subscription_id = data['id']
        # staff_lists = json.loads(event['data']['object']['metadata']['staff'])
        try:
            user = User.objects.get(id=user_id)
            client = CompanyProfile.objects.get(user=user)
            package = Packages.objects.get(id=package_id)
            subscription = Subscription.objects.filter(user=user, package=package, stripe_subscriptoin_id=stripe_subscription_id).first()
            if subscription:
                # subscription.end_date = datetime.fromtimestamp(data['current_period_end'])
                subscription.status = 'active'
                subscription.save()
                # send staff joining mail
                send_staff_joining_mail_task.delay(staff_count, client.id)
        except Exception as e:
            print("Error updating subscription:", e)
            return HttpResponse(status=200)
        return HttpResponse(status=200)
    
    #     print('Customer subscription updated')
    #     data = event['data']['object']
    #     metadata = data.get('metadata', {})
    #     user_id = metadata.get('user_id')
    #     package_id = metadata.get('package_id')
    #     stripe_subscription_id = data['id']
    #     try:
    #         user = User.objects.get(id=user_id)
    #         package = Packages.objects.get(id=package_id)
    #         subscription = Subscription.objects.filter(user=user, package=package, stripe_subscriptoin_id=stripe_subscription_id).first()
    #         if subscription:
    #             subscription.end_date = datetime.fromtimestamp(data['current_period_end'])
    #             # Optionally update status based on the event details.
    #             subscription.save()
    #     except Exception as e:
    #         print("Error updating subscription:", e)
    #     return HttpResponse(status=200)

    # elif event.type == 'customer.subscription.deleted':
    #     print('Customer subscription deleted')
    #     data = event['data']['object']
    #     metadata = data.get('metadata', {})
    #     user_id = metadata.get('user_id')
    #     package_id = metadata.get('package_id')
    #     stripe_subscription_id = data['id']
    #     try:
    #         user = User.objects.get(id=user_id)
    #         package = Packages.objects.get(id=package_id)
    #         subscription = Subscription.objects.filter(user=user, package=package, stripe_subscriptoin_id=stripe_subscription_id).first()
    #         if subscription:
    #             subscription.status = 'cancelled'
    #             subscription.save()
    #     except Exception as e:
    #         print("Error cancelling subscription:", e)
    #     return HttpResponse(status=200)
    
    return HttpResponse(status=403)