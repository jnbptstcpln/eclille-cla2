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
    path('admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
    path('', include("cla_auth.urls")),
    path('', include("cla_public.urls")),
    path('billeterie', include("cla_ticketing.urls")),
    path('privacy/', views.flatpage, {'url': '/privacy/'}, name='privacy'),
    path('legal/', views.flatpage, {'url': '/legal/'}, name='legal'),
    re_path(r'^(?P<url>.*/)$', views.flatpage)  # Catch all URLs and redirect them to flatpage module
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Centrale Lille Associations"

handler400 = 'cla_web.error_views.error_400'
handler403 = 'cla_web.error_views.error_403'
handler404 = 'cla_web.error_views.error_404'
handler500 = 'cla_web.error_views.error_500'
