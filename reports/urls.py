from django.urls import path
from . import views


app_name = "reports"


urlpatterns = [

    path(
        "",
        views.report_dashboard,
        name="dashboard"
    ),

    path(
        "bookings/",
        views.booking_report,
        name="bookings"
    ),

    path(
        "revenue/",
        views.revenue_report,
        name="revenue"
    ),

    path(
        "export/bookings/",
        views.export_bookings_csv,
        name="export_bookings"
    ),

]