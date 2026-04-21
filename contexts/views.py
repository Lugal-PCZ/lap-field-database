from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import render

from .filters import SUFilters, LocaleFilters, LotFilters
from .models import Area, Locale, Lot, Season, SU

# from natsort_rs import natsort

ITEMSPERPAGE = 100


def build_params(request, params):
    paramdict = {}
    for each_param in params:
        paramdict[each_param] = request.GET.get(each_param)
    paramstring = []
    for key, val in paramdict.items():
        if val:
            paramstring.append(f"{key}={val}")
    return paramdict, paramstring


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
        method = "Excavation"
    elif contexttype == "scraping_trenches":
        title = "Scraping Trenches"
        method = "Scraping"
    elif contexttype == "survey_units":
        title = "Survey Units"
        method = "Survey"
    elif contexttype == "surface_findspots":
        title = "Surface Findspots"
        method = "Surface Find"
    all_items = Locale.objects.filter(method=method)
    params, paramstring = build_params(request, ["area"])
    if _ := params["area"]:
        all_items = all_items.filter(area_id=_)
    p = Paginator(all_items, ITEMSPERPAGE)
    if _ := request.GET.get("p"):
        pagenum = int(_) if int(_) <= p.num_pages else p.num_pages
    else:
        pagenum = 1
    context = {
        "title": title,
        "count": p.count,
        "pages": p.get_elided_page_range(pagenum, on_each_side=2, on_ends=1),
        "all_items": p.page(pagenum),
        "params": "&".join(paramstring),
        "form": LocaleFilters(initial=params),
    }
    return render(
        request,
        "contexts/locales_list.html",
        context,
    )


def sus_list(request):
    all_items = SU.objects.exclude(voided=1).prefetch_related(
        Prefetch(
            "seasons",
            Season.objects.all(),
            to_attr="season_list",
        )
    )
    params, paramstring = build_params(request, ["locale", "type", "season"])
    if _ := params["locale"]:
        all_items = all_items.filter(locale_id=_)
    if _ := params["type"]:
        all_items = all_items.filter(prefix_id=_)
    if _ := params["season"]:
        all_items = all_items.filter(seasons__id=_)
    p = Paginator(all_items, ITEMSPERPAGE)
    if _ := request.GET.get("p"):
        pagenum = int(_) if int(_) <= p.num_pages else p.num_pages
    else:
        pagenum = 1
    context = {
        "title": "Stratigraphic Units",
        "count": p.count,
        "pages": p.get_elided_page_range(pagenum, on_each_side=2, on_ends=1),
        "all_items": p.page(pagenum),
        "params": "&".join(paramstring),
        "form": SUFilters(initial=params),
    }
    return render(
        request,
        "contexts/sus_list.html",
        context,
    )


def lots_list(request):
    all_items = Lot.objects.exclude(voided=1)
    params, paramstring = build_params(
        request,
        ["su", "locale", "contents", "season"],
    )
    if _ := request.GET.get("su"):
        all_items = all_items.filter(su_id=_)
    if _ := request.GET.get("locale"):
        all_items = all_items.filter(su__locale_id=_)
    if _ := request.GET.get("contents"):
        all_items = all_items.filter(contents__iexact=_)
    if _ := request.GET.get("season"):
        all_items = all_items.filter(season_id=_)
    p = Paginator(all_items, ITEMSPERPAGE)
    if _ := request.GET.get("p"):
        pagenum = int(_) if int(_) <= p.num_pages else p.num_pages
    else:
        pagenum = 1
    context = {
        "title": "Lots",
        "count": p.count,
        "pages": p.get_elided_page_range(pagenum, on_each_side=2, on_ends=1),
        "all_items": p.page(pagenum),
        "params": "&".join(paramstring),
        "form": LotFilters(initial=params),
    }
    return render(
        request,
        "contexts/lots_list.html",
        context,
    )
