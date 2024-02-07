from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
import djapp.views

handler404 = 'djapp.views.custom_404'
urlpatterns = [
    path('', include('djapp.urls')),
    path('settings/', include('settings.urls')),
    path('bulk/', include('bulk_label.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
