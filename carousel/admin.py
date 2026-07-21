from django.contrib import admin
from .models import Carousel

@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'created_at'
    )

    search_fields = (
        'title',
    )