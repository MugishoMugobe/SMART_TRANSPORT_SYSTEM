from django.db import models

from vehicles.models import Vehicle
from drivers.models import Driver
from routes.models import Route



class Trip(models.Model):

    STATUS_CHOICES = [

        ("SCHEDULED", "Scheduled"),

        ("IN_PROGRESS", "In Progress"),

        ("COMPLETED", "Completed"),

        ("CANCELLED", "Cancelled"),

    ]


    trip_number = models.CharField(

        max_length=30,

        unique=True

    )


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


    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default="SCHEDULED"

    )


    notes = models.TextField(

        blank=True

    )


    created_at = models.DateTimeField(

        auto_now_add=True

    )


    def __str__(self):

        return self.trip_number