from django.db import models
from passengers.models import Passenger
from trips.models import Trip

class Booking(models.Model):

    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Mobile Money', 'Mobile Money'),
        ('Card', 'Card'),
    ]

    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.CASCADE
    )

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE
    )

    seat_number = models.PositiveIntegerField()

    booking_date = models.DateTimeField(
        auto_now_add=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f"{self.passenger} - Seat {self.seat_number}"