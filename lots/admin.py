from django.contrib import admin

from .models import Lot


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = [
        "number",
        "su",
        "contents",
        "season",
    ]
    list_filter = [
        "season",
        "contents",
        "su__locale",
    ]
    search_fields = [
        "number",
    ]
    autocomplete_fields = [
        "su",
    ]
