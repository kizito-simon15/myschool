# project/urls.py  (root URLconf)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import index   # public landing page

urlpatterns = [
    # ----------------------------------------------------------------------
    # PUBLIC PAGES
    # ----------------------------------------------------------------------
    path("", index, name="index"),          #  ←  was “home”, now “index”

    # ----------------------------------------------------------------------
    # APPS THAT REQUIRE AUTHENTICATION
    # ----------------------------------------------------------------------
    path("school/",   include("school.urls")),      # HomeView is named “home” *inside here*
    path("accounts/", include("accounts.urls")),
    path("sms/",      include("sms.urls")),
    path("admin/",    admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
