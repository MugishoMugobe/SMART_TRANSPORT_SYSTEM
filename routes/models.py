from django.db import models

class Route(models.Model):

    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    distance = models.DecimalField(max_digits=6, decimal_places=2)
    estimated_duration = models.DurationField()

    class Meta:
        ordering = ['origin']

    def __str__(self):
        return f"{self.origin} → {self.destination}"