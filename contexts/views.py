from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.db.models.functions import Substr
from django.shortcuts import render

from .models import Area, Locale, Lot, Season, SU

from dal import autocomplete
from natsort_rs import natsort


class LocaleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Locale.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith)
        return qs


def simple_list(request, contexttype):
    if contexttype == "seasons":
        title = Season._meta.verbose_name_plural
        all_items = Season.objects.all()
    elif contexttype == "areas":
        title = Area._meta.verbose_name_plural
        all_items = Area.objects.all()
    context = {
        "title": title,
        "count": len(all_items),
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
    areas = set()
    for item in all_items:
        areas.add((int(item.area_id), str(item.area)))
        filters["area"] = dict(natsort(list(areas), key=lambda _: _[1]))
    if _ := request.GET.get("area"):
        if _ != "all":
            all_items = all_items.filter(area_id=_)
    context = {
        "title": title,
        "count": len(all_items),
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
    locales = set()
    prefixes = set()
    seasons = set()
    for item in all_items:
        locales.add((int(item.locale_id), str(item.locale)))
        filters["locale"] = dict(natsort(list(locales), key=lambda _: _[1]))
        if item.prefix:
            prefixes.add((int(item.prefix_id), str(item.prefix)))
            filters["prefix"] = dict(natsort(list(prefixes), key=lambda _: _[1]))
        for season in item.season_list:
            seasons.add((int(season.id), str(season)))
            filters["season"] = dict(natsort(list(seasons), key=lambda _: _[1]))
    if _ := request.GET.get("locale"):
        if _ != "all":
            all_items = all_items.filter(locale_id=_)
    if _ := request.GET.get("prefix"):
        if _ == "0":
            all_items = all_items.filter(prefix__isnull=True)
        elif _ != "all":
            all_items = all_items.filter(prefix_id=_)
    if _ := request.GET.get("season"):
        if _ != "all":
            all_items = all_items.filter(seasons__id=_)
    p = Paginator(all_items, 200)
    if _ := request.GET.get("p"):
        pagenum = int(_) if int(_) <= p.num_pages else p.num_pages
    else:
        pagenum = 1
    context = {
        "title": "Stratigraphic Units",
        "count": p.count,
        "all_items": p.page(pagenum),
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
    sus = set()
    locales = set()
    contents = set()
    seasons = set()
    for item in all_items:
        sus.add((int(item.su_id), str(item.su)))
        filters["su"] = dict(natsort(list(sus), key=lambda _: _[1]))
        locales.add((int(item.su.locale_id), str(item.su.locale)))
        filters["locale"] = dict(natsort(list(locales), key=lambda _: _[1]))
        contents.add((item.contents, item.contents))
        filters["contents"] = dict(natsort(list(contents), key=lambda _: _[1]))
        seasons.add((int(item.season_id), str(item.season)))
        filters["season"] = dict(natsort(list(seasons), key=lambda _: _[1]))
    if _ := request.GET.get("su"):
        if _ != "all":
            all_items = all_items.filter(su_id=_)
    if _ := request.GET.get("locale"):
        if _ != "all":
            all_items = all_items.filter(su__locale_id=_)
    if _ := request.GET.get("contents"):
        if _ == "0":
            all_items = all_items.filter(contents__isnull=True)
        elif _ != "all":
            all_items = all_items.filter(contents__icontains=_)
    if _ := request.GET.get("season"):
        if _ != "all":
            all_items = all_items.filter(season_id=_)
    p = Paginator(all_items, 200)
    if _ := request.GET.get("p"):
        pagenum = int(_) if int(_) <= p.num_pages else p.num_pages
    else:
        pagenum = 1
    context = {
        "title": Lot._meta.verbose_name_plural,
        "count": p.count,
        "all_items": p.page(pagenum),
        "filters": filters,
    }
    return render(
        request,
        "contexts/lots_list.html",
        context,
    )
