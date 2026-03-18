from django.db.models import Prefetch
from django.db.models.functions import Substr
from django.shortcuts import render

from .models import Area, Locale, Lot, Season, SU


def simple_list(request, contexttype):
    if contexttype == "seasons":
        title = Season._meta.verbose_name_plural
        all_items = Season.objects.all()
    elif contexttype == "areas":
        title = Area._meta.verbose_name_plural
        all_items = Area.objects.all()
    context = {
        "title": title,
        "all_items": all_items,
    }
    return render(
        request,
        "contexts/simple_list.html",
        context,
    )


def locales_list(request, contexttype):
    if contexttype == "excavation_trenches":
        title = "Excavation Trenches"
        all_items = Locale.objects.filter(
            method__in=[
                "Excavation",
            ]
        ).order_by(Substr("name", 1, 7))
    elif contexttype == "scraping_trenches":
        title = "Scraping Trenches"
        all_items = Locale.objects.filter(
            method__in=[
                "Scraping",
            ]
        ).order_by(Substr("name", 1, 7))
    elif contexttype == "survey_units":
        title = "Survey Units"
        all_items = Locale.objects.filter(method="Survey")

    elif contexttype == "surface_findspots":
        title = "Surface Findspots"
        all_items = Locale.objects.filter(method="Surface Find").order_by(
            "area", "name"
        )
    filters = {
        "area": {},
    }
    for item in all_items:
        filters["area"][int(item.area_id)] = str(item.area)
        filters["area"] = {
            key: val
            for key, val in sorted(filters["area"].items(), key=lambda item: item[1])
        }
    if _ := request.GET.get("area"):
        if _ != "all":
            all_items = all_items.filter(area_id=_)
    context = {
        "title": title,
        "all_items": all_items,
        "filters": filters,
    }
    return render(
        request,
        "contexts/locales_list.html",
        context,
    )


def sus_list(request):
    all_items = (
        SU.objects.exclude(voided=1)
        .prefetch_related(
            Prefetch(
                "seasons",
                Season.objects.all(),
                to_attr="season_list",
            )
        )
        .order_by(
            "locus",
            "number",
            "locale",
        )
    )
    filters = {
        "locale": {},
        "prefix": {},
        "season": {},
    }
    for item in all_items:
        filters["locale"][int(item.locale_id)] = str(item.locale)
        filters["locale"] = {
            key: val
            for key, val in sorted(filters["locale"].items(), key=lambda item: item[1])
        }
        if item.prefix:
            filters["prefix"][int(item.prefix_id)] = str(item.prefix)
            filters["prefix"] = {
                key: val
                for key, val in sorted(
                    filters["prefix"].items(), key=lambda item: item[1]
                )
            }
        for season in item.season_list:
            filters["season"][int(season.id)] = str(season)
            filters["season"] = {
                key: val
                for key, val in sorted(
                    filters["season"].items(), key=lambda item: item[1]
                )
            }
    if _ := request.GET.get("locale"):
        if _ != "all":
            all_items = all_items.filter(locale_id=_)
    if _ := request.GET.get("prefix"):
        if _ != "all":
            all_items = all_items.filter(prefix_id=_)
    if _ := request.GET.get("season"):
        if _ != "all":
            all_items = all_items.filter(seasons__id=_)
    context = {
        "title": "Stratigraphic Units",
        "all_items": all_items,
        "filters": filters,
    }
    return render(
        request,
        "contexts/sus_list.html",
        context,
    )


def lots_list(request):
    all_items = Lot.objects.exclude(voided=1).order_by(
        "number",
    )
    filters = {
        "su": {},
        "locale": {},
        "contents": {},
        "season": {},
    }
    for item in all_items:
        filters["su"][int(item.su_id)] = str(item.su)
        filters["su"] = {
            key: val
            for key, val in sorted(filters["su"].items(), key=lambda item: item[1])
        }
        filters["locale"][int(item.su.locale_id)] = str(item.su.locale)
        filters["locale"] = {
            key: val
            for key, val in sorted(filters["locale"].items(), key=lambda item: item[1])
        }
        filters["contents"][item.contents] = str(item.contents)
        filters["contents"] = {
            key: val
            for key, val in sorted(
                filters["contents"].items(), key=lambda item: item[1]
            )
        }
        filters["season"][int(item.season_id)] = str(item.season)
        filters["season"] = {
            key: val
            for key, val in sorted(filters["season"].items(), key=lambda item: item[1])
        }
    if _ := request.GET.get("su"):
        if _ != "all":
            all_items = all_items.filter(su_id=_)
    if _ := request.GET.get("locale"):
        if _ != "all":
            all_items = all_items.filter(su__locale_id=_)
    if _ := request.GET.get("contents"):
        if _ != "all":
            all_items = all_items.filter(contents__icontains=_)
    if _ := request.GET.get("season"):
        if _ != "all":
            all_items = all_items.filter(season_id=_)
    context = {
        "title": Lot._meta.verbose_name_plural,
        "all_items": all_items,
        "filters": filters,
    }
    return render(
        request,
        "contexts/lots_list.html",
        context,
    )
