
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static

UNFOLD = {
    
    
    "DASHBOARD_CALLBACK": "homedashbord.views.dashboard_callback",

     "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": True, 
         
         "navigation": [
            {
                "title": _("Super Admin"), 
                "separator": True,  # Top border
                "collapsible": False, 
                "SITE_TITLE": "Letme Administrator",
                "SITE_HEADER": "Letme Admin Dashboard",
                # "SITE_SUBHEADER": "Appears under SITE_HEADER",
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:index"),
                        # "badge": "homedashbord.views.available_staff_badge",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Users"),
                        "icon": "people",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                    {
                        "title": _("Job Role"),
                        "icon": "engineering",
                        "link": reverse_lazy("admin:users_jobrole_changelist"),
                    },
                    {
                        "title": _("Skills"),
                        "icon": "bolt",
                        "link": reverse_lazy("admin:users_skill_changelist"),
                    },
                    {
                        "title": _("Uniform"),
                        "icon": "person_apron",
                        "link": reverse_lazy("admin:users_uniform_changelist"),
                    },
                    {
                        "title": _("Notifications"),
                        "icon": "notifications_active",
                        "link": reverse_lazy("admin:dashboard_notification_changelist"),
                    },
                    {
                        "title": _("Report and Issue"),
                        "icon": "flag",
                        "link": reverse_lazy("admin:dashboard_report_changelist"),
                    },
                    {
                    "title": _("FAQ"),
                        "icon": "contact_support",
                        "link": reverse_lazy("admin:dashboard_faq_changelist"),
                    },
                    {
                    "title": _("Terms and Conditions"),
                        "icon": "description",
                        "link": reverse_lazy("admin:dashboard_termsandconditions_changelist"),
                    },
                    {
                    "title": _("Letme Review"),
                        "icon": "reviews",
                        "link": reverse_lazy("admin:dashboard_letmereview_changelist"),
                    },
                    {
                    "title": _("Company List"),
                        "icon": "format_list_bulleted",
                        "link": reverse_lazy("admin:dashboard_companylisted_changelist"),
                    },
                ],
            },
            {
                "title": _("Company Profile"),
                "icon": "apartment",
                "collapsible": False, 
                "items":[
                    {
                        "title": _("Profile"),
                        "icon": "apartment",
                        "link": reverse_lazy("admin:client_companyprofile_changelist"),
                    },
                    {
                        "title": _("Jobs"),
                        "icon": "work",
                        "link": reverse_lazy("admin:client_job_changelist"),
                    },
                    {
                        "title": _("Vacancies"),
                        "icon": "work",
                        "link": reverse_lazy("admin:client_vacancy_changelist"),
                    },
                    {
                        "title": _("Checkin"),
                        "icon": "check",
                        "link": reverse_lazy("admin:client_checkin_changelist"),
                    },
                    {
                        "title": _("Checkout"),
                        "icon": "done_all",
                        "link": reverse_lazy("admin:client_checkout_changelist"),
                    },
                    {
                        "title": _("Favourite Staff"),
                        "icon": "star",
                        "link": reverse_lazy("admin:client_favouritestaff_changelist"),
                    },
                    {
                        "title": _("My Own Staff"),
                        "icon": "location_away",
                        "link": reverse_lazy("admin:client_mystaff_changelist"),
                    },
                    {
                        "title": _("Job Ads"),
                        "icon": "ads_click",
                        "link": reverse_lazy("admin:client_jobads_changelist"),
                    },
                    {
                        "title": _("Job Application"),
                        "icon": "inventory",
                        "link": reverse_lazy("admin:client_jobapplication_changelist"),
                    },
                    {
                        "title": _("Job Report"),
                        "icon": "work_history",
                        "link": reverse_lazy("admin:client_jobreport_changelist"),
                    },
                    {
                        "title": _("Review"),
                        "icon": "reviews",
                        "link": reverse_lazy("admin:client_companyreview_changelist"),
                    }
                ]
            },
            {
                "title": _("Staff Profile"),
                "icon": "apartment",
                "collapsible": False, 
                "items":[
                    {
                        "title": _("Staff"),
                        "icon": "id_card",
                        "badge": "homedashbord.views.available_staff_badge",
                        "link": reverse_lazy("admin:staff_staff_changelist"),
                    },
                    {
                        "title": _("Experiences"),
                        "icon": "emoji_objects",
                        "link": reverse_lazy("admin:staff_experience_changelist"),
                    },
                    {
                        "title": _("Review"),
                        "icon": "reviews",
                        "link": reverse_lazy ("admin:staff_staffreview_changelist"),
                    }
                ]
            },
            
        ],
    },

    "STYLES": [
        lambda request: static("css/custom_unfold.css"),
    ],

    "SCRIPTS": [
        lambda request: static("js/custom_unfold.js"),
        lambda request: static("js/pie_chart_unfold.js"),
    ],

}

