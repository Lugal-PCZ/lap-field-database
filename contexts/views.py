from django.db.models import Prefetch
from django.db.models.functions import Substr
from django.shortcuts import render

from .models import Area, Locale, Lot, Season, SU


def simple_list(request, contexttype):
    if contexttype == "seasons":
        all_items = Season.objects.all()
        title = Season._meta.verbose_name_plural
    elif contexttype == "areas":
        all_items = Area.objects.all()
        title = Area._meta.verbose_name_plural
    context = {
        "all_items": all_items,
        "title": title,
    }
    return render(
        request,
        "contexts/simple_list.html",
        context,
    )


def locales_list(request, contexttype):
    if contexttype == "excavation_trenches":
        all_items = Locale.objects.filter(
            method__in=[
                "Excavation",
            ]
        ).order_by(Substr("name", 1, 7))
        title = "Excavation Trenches"
    elif contexttype == "scraping_trenches":
        all_items = Locale.objects.filter(
            method__in=[
                "Scraping",
            ]
        ).order_by(Substr("name", 1, 7))
        title = "Scraping Trenches"
    elif contexttype == "survey_units":
        all_items = Locale.objects.filter(method="Survey")
        title = "Survey Units"
    elif contexttype == "surface_findspots":
        all_items = Locale.objects.filter(method="Surface Find").order_by(
            "area", "name"
        )
        title = "Surface Findspots"
    context = {
        "all_items": all_items,
        "title": title,
    }
    return render(
        request,
        "contexts/locales_list.html",
        context,
    )


def sus_list(request):
    all_items = (
        SU.objects.prefetch_related(
            Prefetch("seasons", Season.objects.all(), to_attr="season_list")
        )
        .exclude(voided=1)
        .order_by("locus", "number", "locale")
    )
    context = {
        "all_items": all_items,
        "title": "Stratigraphic Units",
    }
    return render(
        request,
        "contexts/sus_list.html",
        context,
    )


def lots_list(request):
    all_items = Lot.objects.exclude(voided=1)
    context = {
        "all_items": all_items,
        "title": Lot._meta.verbose_name_plural,
    }
    return render(
        request,
        "contexts/lots_list.html",
        context,
    )
