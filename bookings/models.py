from io import BytesIO

import qrcode

from django.core.files import File
from django.db import models

from passengers.models import Passenger
from trips.models import Trip



class Booking(models.Model):

    STATUS_CHOICES = [

        ("CONFIRMED", "Confirmed"),

        ("CANCELLED", "Cancelled"),

    ]


    booking_reference = models.CharField(

        max_length=20,

        unique=True,

        editable=False

    )


    passenger = models.ForeignKey(

        Passenger,

        on_delete=models.CASCADE,

        related_name="bookings"

    )


    trip = models.ForeignKey(

        Trip,

        on_delete=models.CASCADE,

        related_name="bookings"

    )


    # Selected seat from interactive seat map

    seat_number = models.PositiveIntegerField()



    amount = models.DecimalField(

        max_digits=10,

        decimal_places=2

    )


    booking_date = models.DateTimeField(

        auto_now_add=True

    )


    payment_status = models.BooleanField(

        default=True

    )


    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default="CONFIRMED"

    )


    qr_code = models.ImageField(

        upload_to="qrcodes/",

        blank=True,

        null=True

    )


    class Meta:

        ordering = [

            "-booking_date"

        ]


    def __str__(self):

        return self.booking_reference



    # -----------------------------------------
    # Generate QR Code
    # -----------------------------------------

    def generate_qr_code(self):


        qr = qrcode.QRCode(

            version=1,

            box_size=10,

            border=4

        )


        qr_data = f"""

Smart Public Transport System

Booking Reference:
{self.booking_reference}

Passenger:
{self.passenger.full_name}

Trip:
{self.trip.trip_number}

Route:
{self.trip.route.origin}
to
{self.trip.route.destination}

Seat:
{self.seat_number}

Amount:
{self.amount}

Status:
{self.status}

"""


        qr.add_data(qr_data)


        qr.make(
            fit=True
        )


        image = qr.make_image(

            fill_color="black",

            back_color="white"

        )


        buffer = BytesIO()


        image.save(

            buffer,

            format="PNG"

        )


        filename = (

            f"{self.booking_reference}.png"

        )


        self.qr_code.save(

            filename,

            File(buffer),

            save=False

        )



    # -----------------------------------------
    # Save Booking
    # -----------------------------------------

    def save(self, *args, **kwargs):


        creating = self.pk is None


        super().save(*args, **kwargs)



        if creating and not self.qr_code:


            self.generate_qr_code()


            super().save(

                update_fields=[

                    "qr_code"

                ]

            )