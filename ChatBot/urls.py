
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from chat.views import RegisterView



urlpatterns = [
    path('admin/', admin.site.urls),
    path("chat/", include('chat.urls')),
    path("account/", include('django.contrib.auth.urls')),
    path("account/register/", RegisterView.as_view(), name="register"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
