from django.contrib import admin

from .models import Area, Locale, Lot, Season, SU, SUPrefix


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "shortname",
    ]
    ordering = [
        "name",
    ]


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


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "year",
        "timeofyear",
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
    ordering = [
        "number",
        "locus",
        "locale",
    ]
    autocomplete_fields = [
        "locale",
    ]

    @admin.display(description="Feature Type")
    def feature_type(self, obj):
        return obj.prefix

    @admin.display(description="Season(s)")
    def season_list(self, obj):
        return ", ".join([season.name for season in obj.seasons.all()])


@admin.register(SUPrefix)
class SUPrefixAdmin(admin.ModelAdmin):
    list_display = [
        "prefix",
        "feature",
    ]
