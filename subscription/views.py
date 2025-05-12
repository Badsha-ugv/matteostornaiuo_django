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
from utility.utils import send_staff_invitation
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
    
# @csrf_exempt
# @api_view(['POST'])
# def package_checkout(request,pkg_id):
#         if not request.user.is_authenticated:
#             return Response({"error": "You need to be logged in to checkout"}, status=status.HTTP_401_UNAUTHORIZED)
#         user = request.user
#         # data = request.data

#         if user.is_client:
#             client = CompanyProfile.objects.get(user=user)
#         try:
#             package = Packages.objects.get(id=pkg_id)
#         except Packages.DoesNotExist:
#             return Response({"error": "Package not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         # Create a customer
#         try:
#         # Search for existing customer by email
#             customers = stripe.Customer.list(email=user.email, limit=1)
#             if customers.data:
#                 stripe_customer = customers.data[0]
#             else:
#                 # Create new customer if not found
#                 stripe_customer = stripe.Customer.create(
#                     email=user.email,
#                     name=f"{user.first_name} {user.last_name}"
#                 )
#         except stripe.error.StripeError as e:
#             # Handle any Stripe API errors
            
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
#         # get current subscription
#         try:
#             current_subscription = Subscription.objects.get(user=user, status='active')
#             stripe_subscription = stripe.Subscription.retrieve(current_subscription.stripe_subscriptoin_id)
#         except Subscription.DoesNotExist:
#             current_subscription = None
#             stripe_subscription = None

#         # Cancel current subscription if exists and not up to date
#         if stripe_subscription:
#             try:
#                 update_subscription = stripe.Subscription.modify(
#                     stripe_subscription.id,
#                     items=[{
#                         'id': stripe_subscription['items']['data'][0].id,
#                         'price': package.stripe_price_id
#                     }],
#                     proration_behavior='create_prorations',
#                 )
#                 current_subscription.status = 'cancelled'
#                 current_subscription.save()

#                 new_subscription = Subscription.objects.create(
#                     user=user,
#                     package=package,
#                     stripe_subscriptoin_id=update_subscription.id,
#                     end_date=datetime.fromtimestamp(update_subscription['current_period_end']),
#                     status='active',
#                 )
#                 response = {
#                     "message": "Subscription cancelled and new subscription created",
#                     "subscription_id": new_subscription.id,
#                     "subscription_end_date": new_subscription.end_date.strftime('%Y-%m-%d %H:%M:%S')
#                 }
#                 return Response(response, status=status.HTTP_200_OK)
            
            
#             except stripe.error.StripeError as e:
#                 # Handle any Stripe API errors
#                 return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             try:
#                 checkout_session = stripe.checkout.Session.create(
#                     payment_method_types=['card'],
#                     mode='subscription',
#                     line_items=[{'price':package.stripe_price_id, 'quantity': 1}],
#                     customer=stripe_customer.id,
#                     success_url=settings.STRIPE_SUCCESS_URL,
#                     cancel_url=settings.STRIPE_CANCEL_URL,
#                     # save card for next pay
#                     saved_payment_method_options={"payment_method_save": "enabled"},
#                     metadata={'package_id': str(package.id), 'user_id': str(user.id)},
#                     subscription_data={
#                     'metadata': {
#                         'user_id':str(user.id),
#                         'package_id': str(package.id),
#                     }
#                 },

#                 )
#                 # return checkout url, success url, cancel url with success message
#                 response = {
#                     "message": "Checkout session created",
#                     "url": checkout_session.url,
#                     "success_url": settings.STRIPE_SUCCESS_URL,
#                     "cancel_url": settings.STRIPE_CANCEL_URL,
                    
#                 }
#                 return Response(response, status=status.HTTP_200_OK)
            
#             except stripe.error.StripeError as e:
#                 # Handle any Stripe API errors
#                 return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        

# @csrf_exempt
# def webhook(request):
#     print('webhook called')
#     payload = request.body
#     sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
#     endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
#     event = None

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#         print('Webhook event type:', event.type)
#         # print('event', event)
#     except Exception as e:
#         print('Error deserializing webhook:', e)
#         return HttpResponse(status=400)
    
    
#     if event.type == 'customer.subscription.created':
#         print('Customer subscription created')
#         data = event['data']['object'] 
#         metadata = data.get('metadata', {})
#         user_id = metadata.get('user_id')
#         package_id = metadata.get('package_id')
#         stripe_subscription_id = data['id']

#         print('user id sub', user_id, package_id, stripe_subscription_id)

#         user = User.objects.filter(id=user_id).first()
#         package = Packages.objects.get(id=package_id)

#         print('userr', user)
#         print('package', package)

#         Subscription.objects.create(
#             user=user,
#             package=package,
#             stripe_subscriptoin_id=stripe_subscription_id,
#             # start_date=data['current_period_start'],
#             end_date=datetime.fromtimestamp(data['current_period_end']),
#             # status='active',
#         )

#         return HttpResponse(status=200)
    
#     elif event.type == 'customer.subscription.updated':
#         print('Customer subscription updated')
#         data = event['data']['object']
#         print('data', data)
#         metadata = data.get('metadata', {})
#         user_id = metadata.get('user_id')
#         package_id = metadata.get('package_id')
#         stripe_subscription_id = data['id']
        
#         print('user id sub', user_id, package_id, stripe_subscription_id)
#         user = User.objects.filter(id=user_id).first()
#         package = Packages.objects.get(id=package_id)
#         subscription = Subscription.objects.filter(user=user, package=package, stripe_subscriptoin_id=stripe_subscription_id).first()
#         subscription.status = 'active'
#         subscription.save()
#         return HttpResponse(status=200)
    
#     elif event.type == 'customer.subscription.deleted':
#         print('Customer subscription deleted')
#         data = event['data']['object']
#         metadata = data.get('metadata', {})
#         user_id = metadata.get('user_id')
#         package_id = metadata.get('package_id')
#         stripe_subscription_id = data['id']
#         print('user id sub', user_id, package_id, stripe_subscription_id)
#         user = User.objects.filter(id=user_id).first()
#         package = Packages.objects.get(id=package_id)
#         subscription = Subscription.objects.filter(user=user, package=package, stripe_subscriptoin_id=stripe_subscription_id).first()
#         subscription.status = 'cancelled'
#         subscription.save()
#         return HttpResponse(status=200)
    

#     return HttpResponse(status=403)




@csrf_exempt
@api_view(['POST'])
def package_checkout(request, pkg_id):
    if not request.user.is_authenticated:
        return Response({"error": "You need to be logged in to checkout"}, status=status.HTTP_401_UNAUTHORIZED)
    
    user = request.user

    # Retrieve package or return 404
    try:
        package = Packages.objects.get(id=pkg_id)
    except Packages.DoesNotExist:
        return Response({"error": "Package not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Create or retrieve Stripe customer
    try:
        customers = stripe.Customer.list(email=user.email, limit=1)
        if customers.data:
            stripe_customer = customers.data[0]
        else:
            stripe_customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}"
            )
    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Check for an existing active subscription
    try:
        current_subscription = Subscription.objects.get(user=user, status='active')
        stripe_subscription = stripe.Subscription.retrieve(current_subscription.stripe_subscriptoin_id)
    except Subscription.DoesNotExist:
        current_subscription = None
        stripe_subscription = None

    if stripe_subscription:
        try:
            # Modify subscription to update to the new package price,
            # enable proration, and generate a Payment Intent for any proration invoice.
            updated_subscription = stripe.Subscription.modify(
                stripe_subscription.id,
                items=[{
                    'id': stripe_subscription['items']['data'][0].id,
                    'price': package.stripe_price_id
                }],
                proration_behavior='create_prorations',
                payment_behavior='default_incomplete',  # Creates a Payment Intent if payment is required (proration)
                payment_settings={
                    'save_default_payment_method': 'on_subscription',
                },
                expand=['latest_invoice.payment_intent'],
            )
            # Mark the previous subscription as cancelled locally
            current_subscription.status = 'cancelled'
            current_subscription.save()

            # Create a new subscription record locally (status pending until payment confirmation)
            new_subscription = Subscription.objects.create(
                user=user,
                package=package,
                stripe_subscriptoin_id=updated_subscription.id,
                end_date=datetime.fromtimestamp(updated_subscription['current_period_end']),
                status='pending',  # pending until the Payment Intent is confirmed via webhook
            )

            # Retrieve Payment Intent client secret from the latest invoice
            payment_intent = updated_subscription.latest_invoice.get('payment_intent')
            client_secret = payment_intent.get('client_secret') if payment_intent else None

            return Response({
                "message": "Subscription updated. Please confirm payment.",
                "subscription_id": new_subscription.id,
                "subscription_end_date": new_subscription.end_date.strftime('%Y-%m-%d %H:%M:%S'),
                "clientSecret": client_secret,
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        try:
            # Create a new subscription in an incomplete state with an attached Payment Intent.
            new_subscription = stripe.Subscription.create(
                customer=stripe_customer.id,
                items=[{'price': package.stripe_price_id}],
                payment_behavior='default_incomplete',  # Creates Payment Intent for the first invoice
                expand=['latest_invoice.payment_intent'],
                payment_settings={
                    'save_default_payment_method': 'on_subscription',
                },
                metadata={
                    'user_id': str(user.id),
                    'package_id': str(package.id),
                }
            )
            payment_intent = new_subscription.latest_invoice.get('payment_intent')
            client_secret = payment_intent.get('client_secret') if payment_intent else None

            # Create a local subscription record with status pending until payment confirmation.
            Subscription.objects.create(
                user=user,
                package=package,
                stripe_subscriptoin_id=new_subscription.id,
                end_date=datetime.fromtimestamp(new_subscription['current_period_end']),
                status='pending',
            )

            return Response({
                "message": "Subscription created. Please confirm the payment.",
                "subscription_id": new_subscription.id,
                "clientSecret": client_secret,
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --------------------- WEBHOOK HANDLER ---------------------
@csrf_exempt
def webhook(request):
    print('Webhook called')
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
        print('Customer subscription created')
        data = event['data']['object']
        metadata = data.get('metadata', {})
        print('metadata', metadata)
        user_id = metadata.get('user_id')
        package_id = metadata.get('package_id')
        obj = json.loads(event['data']['object']['metadata']['staff'])
        print('obj', obj)
        stripe_subscription_id = data['id']


        try:
            user = User.objects.get(id=user_id)
            client = CompanyProfile.objects.get(user=user)
            package = Packages.objects.get(id=package_id)
            Subscription.objects.create(
                user=user,
                package=package,
                stripe_subscriptoin_id=stripe_subscription_id,
                end_date=datetime.fromtimestamp(data['current_period_end']),
                status='active',  # Will be updated to active after payment succeeds
            )

            # send staff joining mail
            send_staff_joining_mail_task.delay(obj, client.id)
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
        print('metadata', metadata)
        user_id = metadata.get('user_id')
        print('user id', user_id)
        package_id = metadata.get('package_id')
        print('package id', package_id)
        stripe_subscription_id = data['id']
        staff_lists = json.loads(event['data']['object']['metadata']['staff'])
        print('staff_lists', staff_lists)
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
                send_staff_joining_mail_task.delay(staff_lists, client.id)
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