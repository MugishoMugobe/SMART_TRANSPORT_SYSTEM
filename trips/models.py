from django.db import models
from vehicles.models import Vehicle
from drivers.models import Driver
from routes.models import Route

class Trip(models.Model):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE
    )

    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE
    )

    departure_time = models.DateTimeField()

    arrival_time = models.DateTimeField()

    available_seats = models.PositiveIntegerField()

    fare = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    STATUS = [
        ('Scheduled', 'Scheduled'),
        ('Departed', 'Departed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='Scheduled'
    )

    class Meta:
        ordering = ['departure_time']

    def __str__(self):
        return f"{self.route} ({self.departure_time})"