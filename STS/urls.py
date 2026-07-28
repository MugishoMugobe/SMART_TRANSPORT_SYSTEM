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
from django.conf.urls.static import static
from django.views.generic import RedirectView

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

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# can be put in any page on loading
admin.site.site_header = "Smart Public Transport Management"
admin.site.site_title = "Transport Admin"
admin.site.index_title = "Administration Dashboard"

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )