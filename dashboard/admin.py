from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter, RangeDateTimeFilter

from .models import  Notification, Report, FAQ, TermsAndConditions, LetmeReview, CompanyListed


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('user', 'created_at', 'is_read', 'message')
    list_editable = ('is_read', )


@admin.register(Report)
class ReportAdmin(ModelAdmin):
    list_display = ('user', 'type', 'created_at','is_resolved')
    # list_editable = ('type', )
    search_fields = ('user__first_name', 'user__last_name', 'type')
    list_filter = (
        ('created_at', RangeDateTimeFilter),
        ('user', admin.RelatedOnlyFieldListFilter),
    )

@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ('question','answer')
    search_fields = ('question', 'answer')

@admin.register(TermsAndConditions)
class TermsAndConditionsAdmin(ModelAdmin):
    pass 

@admin.register(LetmeReview)
class LetmeReviewAdmin(ModelAdmin):
    list_display = ('image_view','reviewer', 'designation', 'is_publish','review_view', 'created_at')
    search_fields = ('reviewer', 'designation')
    list_display_links = ('image_view','reviewer')

    def image_view(self, obj):
        return format_html(
            '<img src="{}" width="100px" height="100px">',
            obj.image.url if obj.image else None
        )
    image_view.short_description = 'Image'
    image_view.allow_tags = True

    # show  only 50 word from review
    def review_view(self, obj):
        return obj.review[:50] + '...' if obj.review else None
    review_view.short_description = 'Review'
    review_view.allow_tags = True
    

@admin.register(CompanyListed)
class CompanyListedAdmin(ModelAdmin):
    list_display = ('company', 'order', 'is_show')
    search_fields = ('company__company_name',)
    list_filter_sheet = False
    list_filter = (
        ('company', admin.RelatedOnlyFieldListFilter),
        ('is_show', admin.BooleanFieldListFilter),
    )