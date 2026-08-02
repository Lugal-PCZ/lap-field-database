from django.contrib import admin
from django.db.models import F

from .models import Locale, SU, SUPrefix


@admin.register(Locale)
class LocaleAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "method",
        "area",
    ]
    list_filter = [
        "method",
        "area",
    ]
    search_fields = [
        "name",
    ]
    ordering = [
        F("name")[0:6],
        "id",
    ]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if "/autocomplete/" not in request.get_full_path():
            return queryset, use_distinct
        else:
            return queryset.exclude(method="Survey"), True


@admin.register(SU)
class SUAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "locale__name",
        "feature_type",
        "season_list",
    ]
    list_filter = [
        "seasons",
        "locale__method",
        "prefix__feature",
    ]
    search_fields = [
        "number",
        "locus",
        "locale__name",
    ]
    autocomplete_fields = [
        "locale",
    ]

    @admin.display(description="Feature Type")
    def feature_type(self, obj):
        return obj.prefix

    @admin.display(description="Seasons")
    def season_list(self, obj):
        return ", ".join([season.name for season in obj.seasons.all()])

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if "/autocomplete/" not in request.get_full_path():
            return queryset, use_distinct
        else:
            return queryset.exclude(locale__method="Survey").exclude(locus__isnull=False).exclude(voided=True), True


@admin.register(SUPrefix)
class SUPrefixAdmin(admin.ModelAdmin):
    list_display = [
        "prefix",
        "feature",
    ]
