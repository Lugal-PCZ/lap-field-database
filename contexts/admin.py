from django.contrib import admin

from .models import Area, Locale, Lot, Season, SU, SUPrefix


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ["name", "shortname"]
    ordering = ["name"]


@admin.register(Locale)
class LocaleAdmin(admin.ModelAdmin):
    list_display = ["name", "method", "area", "season_list"]
    list_filter = ["method", "area", "seasons"]

    def season_list(self, obj):
        return ", ".join([season.name for season in obj.seasons.all()])

    season_list.short_description = "Seasons"


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    pass


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ["name", "year", "timeofyear"]


@admin.register(SU)
class SUAdmin(admin.ModelAdmin):
    list_display = ["number", "locale", "season_list"]
    list_filter = ["seasons", "locale"]

    def season_list(self, obj):
        return ", ".join([season.name for season in obj.seasons.all()])

    season_list.short_description = "Seasons"


@admin.register(SUPrefix)
class SUPrefixAdmin(admin.ModelAdmin):
    list_display = ["prefix", "feature"]
