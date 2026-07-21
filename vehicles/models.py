from django.db import models

class Vehicle(models.Model):

    BUS = "Bus"
    TAXI = "Taxi"
    MINIBUS = "Minibus"

    VEHICLE_TYPES = [
        (BUS, "Bus"),
        (TAXI, "Taxi"),
        (MINIBUS, "Minibus"),
    ]

    vehicle_number = models.CharField(max_length=100, unique=True)
    vehicle_type = models.CharField(
        max_length=50,
        choices=VEHICLE_TYPES
    )
    seating_capacity = models.PositiveIntegerField()
    model = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    image = models.ImageField(upload_to='vehicles/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['vehicle_number']

    def __str__(self):
        return self.vehicle_number