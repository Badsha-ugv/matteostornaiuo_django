
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls

# admin.site.site_title = "Company Name"
# admin.site.site_header = "matteostornaiuo"
# admin.site.index_title = "Welcome to Company Admin"

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/', include('users.urls')),
    # path('api/', include('client.urls') ),
    # path('api/', include('staff.urls')),
    # path('api/', include('dashboard.urls')),
    # path('api/', include('chat.urls')),
    # path('api/', include('shifting.urls')),
    # path('api/', include('subscription.urls')),
    # path('api/', include('homedashbord.urls')),
    # path('api/', include('celeryapi.urls')),

    path('api/v1/', include('api.app.urls')),
    path('api/v1/',include('api.web.urls')),
    

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    

] + debug_toolbar_urls()

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)