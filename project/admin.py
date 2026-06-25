from django.contrib import admin

from .models import Area, Season


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "shortname",
    ]


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "year",
        "timeofyear",
    ]
