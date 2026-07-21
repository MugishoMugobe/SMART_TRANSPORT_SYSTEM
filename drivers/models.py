from django.db import models

class Driver(models.Model):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=100, unique=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    photo = models.ImageField(upload_to='drivers/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name