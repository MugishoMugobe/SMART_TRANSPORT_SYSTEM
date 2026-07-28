from django.db import models


class Route(models.Model):

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
    ]

    origin = models.CharField(max_length=200)

    destination = models.CharField(max_length=200)

    distance = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    estimated_duration = models.DurationField()

    fare = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.origin} → {self.destination}"