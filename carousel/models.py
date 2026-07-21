from django.db import models

class Carousel(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to='carousel/'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title