"""cla_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.flatpages import views

from cla_auth.views.session import login

urlpatterns = [
    path("admin/login/", login),  # Override default login
    path("admin/", admin.site.urls),
    # Dependencies
    path("summernote/", include("django_summernote.urls")),
    path("qr_code/", include("qr_code.urls", namespace="qr_code")),
    # Project's apps
    path("", include("cla_auth.urls")),
    path("", include("cla_public.urls")),
    path("", include("cla_registration.urls")),
    path("espace-adherent/", include("cla_member.urls")),
    path("billetteries/", include("cla_ticketing.urls")),
    path("associations/", include("cla_association.urls")),
    path("evenements/", include("cla_event.urls")),
    path("reservations/", include("cla_reservation.urls")),
    # Flat pages
    path("privacy/", views.flatpage, {"url": "/privacy/"}, name="privacy"),
    path("legal/", views.flatpage, {"url": "/legal/"}, name="legal"),
    path("faq/", views.flatpage, {"url": "/faq/"}, name="faq"),
    re_path(
        r"^(?P<url>.*/)$", views.flatpage
    ),  # Catch all URLs and redirect them to flatpage module
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Centrale Lille Associations"
admin.site.site_title = "Espace d'administration"

handler400 = "cla_web.error_views.error_400"
handler403 = "cla_web.error_views.error_403"
handler404 = "cla_web.error_views.error_404"
handler500 = "cla_web.error_views.error_500"
