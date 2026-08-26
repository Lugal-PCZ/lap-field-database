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


@admin.register(SUPrefix)
class SUPrefixAdmin(admin.ModelAdmin):
    list_display = [
        "prefix",
        "feature",
    ]
