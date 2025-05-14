from django.contrib import admin
from unfold.admin import ModelAdmin



from .models import Packages, Subscription


@admin.register(Packages)
class PackageAdmin(ModelAdmin):
    list_display = ('name', 'price', 'number_of_staff', 'duration', 'is_active', 'created_at')

@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ('user', 'package__name', 'status', 'start_date', 'end_date')
    list_filter = ('package__name', 'status')
    list_filter_sheet = False
    search_fields = ('user__first_name', 'user__last_name', 'package__name')
    date_hierarchy ='start_date'
    ordering = ['-created_at']
    
