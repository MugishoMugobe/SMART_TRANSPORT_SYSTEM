"""
URL configuration for STS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView
from django.views.static import serve as serve_media

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("passengers/", include("passengers.urls")),
    path("drivers/", include("drivers.urls")),
    path("vehicles/", include("vehicles.urls")),
    path("routes/", include("routes.urls")),
    path("trips/", include("trips.urls")),
    path("bookings/", include("bookings.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("", RedirectView.as_view(url="/dashboard/")),
    path("reports/", include("reports.urls")),

    path("api/v1/", include("api.urls")),
    path("api-auth/", include("rest_framework.urls")),  # browsable API login/logout

    # Uploaded driver/vehicle photos and booking QR codes. Deliberately
    # unconditional (not gated behind DEBUG) — Django's static() helper
    # only ever serves media in debug mode, which would 404 every upload
    # in production. django.views.static.serve isn't built for
    # high-traffic use, but it's the right tradeoff at this project's
    # scale versus standing up a separate file host.
    path(
        f"{settings.MEDIA_URL.lstrip('/')}<path:path>",
        serve_media,
        {"document_root": settings.MEDIA_ROOT},
    ),
]

admin.site.site_header = "Smart Public Transport Management"
admin.site.site_title = "Transport Admin"
admin.site.index_title = "Administration Dashboard"