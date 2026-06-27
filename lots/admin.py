from django.contrib import admin

from .models import Lot


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = [
        "number",
        "su",
        "su__locale",
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

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if "/autocomplete/" not in request.get_full_path():
            return queryset, use_distinct
        else:
            return queryset.exclude(voided=True), True
