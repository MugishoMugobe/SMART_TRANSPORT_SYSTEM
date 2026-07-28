from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.db.models import Sum, Count

from bookings.models import Booking
from trips.models import Trip
from passengers.models import Passenger



@login_required
def report_dashboard(request):

    total_bookings = Booking.objects.count()

    total_revenue = Booking.objects.filter(
        status="CONFIRMED"
    ).aggregate(
        Sum("amount")
    )["amount__sum"] or 0


    total_passengers = Passenger.objects.count()


    total_trips = Trip.objects.count()


    context = {

        "total_bookings": total_bookings,

        "total_revenue": total_revenue,

        "total_passengers": total_passengers,

        "total_trips": total_trips,

    }


    return render(

        request,

        "reports/report_dashboard.html",

        context

    )



@login_required
def booking_report(request):

    bookings = Booking.objects.select_related(

        "passenger",

        "trip"

    ).all()


    return render(

        request,

        "reports/booking_report.html",

        {

            "bookings": bookings

        }

    )



@login_required
def revenue_report(request):

    revenue = Booking.objects.filter(

        status="CONFIRMED"

    ).aggregate(

        total=Sum("amount")

    )


    return render(

        request,

        "reports/revenue_report.html",

        {

            "revenue": revenue["total"] or 0

        }

    )



@login_required
def export_bookings_csv(request):

    import csv

    from django.http import HttpResponse


    response = HttpResponse(

        content_type="text/csv"

    )


    response["Content-Disposition"] = (

        'attachment; filename="bookings.csv"'

    )


    writer = csv.writer(response)


    writer.writerow([

        "Reference",

        "Passenger",

        "Trip",

        "Seat",

        "Amount",

        "Date"

    ])



    bookings = Booking.objects.all()



    for booking in bookings:

        writer.writerow([

            booking.booking_reference,

            booking.passenger.full_name,

            booking.trip.trip_number,

            booking.seat_number,

            booking.amount,

            booking.booking_date,

        ])



    return response