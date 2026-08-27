from django.core.paginator import Paginator
from django.db.models import F, Prefetch
from django.shortcuts import render

from lapinfo.models import Season
from ..models import Locale, SU
from ..forms import SUFilters, LocaleFilters


ITEMSPERPAGE = 100


def _build_params(request, params):
    paramdict = {}
    for each_param in params:
        paramdict[each_param] = request.GET.get(each_param)
    paramlist = []
    for key, val in paramdict.items():
        if val:
            paramlist.append(f"{key}={val}")
    paramstring = ""
    if paramlist:
        paramstring = f"&{'&'.join(paramlist)}"
    return paramdict, paramstring


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
    unfiltered_items = (
        Locale.objects.filter(method=method)
        .extra(
            select={
                "sortorder": 'CASE WHEN "method" = "Survey" THEN "b-" || "name" WHEN "method" = "Surface Find" THEN "c-" || "name" WHEN substr("name", "LAPTT") THEN "a-" || "name" ELSE cast(substr("name", instr("name", " ") + 1, 3) as int) END'
            }
        )
        .order_by("sortorder")  # type: ignore
        .prefetch_related(
            Prefetch(
                "sus",
                queryset=SU.objects.prefetch_related(
                    Prefetch(
                        "seasons",
                        queryset=Season.objects.all(),
                        to_attr="seasons_list",
                    )
                ),
                to_attr="sus_list",
            )
        )
    )
    params, paramstring = _build_params(request, ["area", "season"])
    for each_item in unfiltered_items:
        seasons = []
        seasons_list = set()
        for each_su in each_item.sus_list:  # type: ignore
            if each_su.seasons.values():
                seasons.append(each_su.seasons.values()[0]["id"])
                seasons_list.add(each_su.seasons.values()[0]["name"])
        seasons_list = list(seasons_list)
        seasons_list.sort()
        each_item.seasons = seasons  # type: ignore
        each_item.seasons_list = seasons_list  # type: ignore
    filtered_items = unfiltered_items
    if area := params["area"]:
        filtered_items = [item for item in filtered_items if item.area_id == int(area)]  # type: ignore
    if season := params["season"]:
        refiltered_items = []
        for each_item in filtered_items:
            if int(season) in each_item.seasons:  # type: ignore
                refiltered_items.append(each_item)
        filtered_items = refiltered_items
    p = Paginator(filtered_items, ITEMSPERPAGE)
    if pagenum := request.GET.get("p"):
        pagenum = int(pagenum) if int(pagenum) <= p.num_pages else p.num_pages
    else:
        pagenum = 1
    context = {
        "view": "list",
        "title": title,
        "newitemlink": "/locale/new/",
        "count": p.count,
        "pages": p.get_elided_page_range(pagenum, on_each_side=2, on_ends=1),  # type: ignore
        "all_items": p.page(pagenum),
        "params": paramstring,
        "form": LocaleFilters(initial=params),
    }
    return render(
        request,
        "contexts/locales_list.html",
        context,
    )


def sus_list(request):
    unfiltered_items = SU.objects.prefetch_related(
        Prefetch(
            "seasons",
            queryset=Season.objects.all(),
            to_attr="seasons_list",
        )
    )
    params, paramstring = _build_params(request, ["locale", "type", "season"])
    filtered_items = unfiltered_items
    if locale := params["locale"]:
        filtered_items = [item for item in filtered_items if item.locale_id == int(locale)]  # type: ignore
    if type := params["type"]:
        filtered_items = [item for item in filtered_items if item.prefix_id == int(type)]  # type: ignore
    if season := params["season"]:
        refiltered_items = []
        for each_item in filtered_items:
            seasons = []
            for each_season in each_item.seasons_list:  # type: ignore
                seasons.append(each_season.id)
            if int(season) in seasons:
                refiltered_items.append(each_item)
        filtered_items = refiltered_items
    p = Paginator(filtered_items, ITEMSPERPAGE)
    if pagenum := request.GET.get("p"):
        pagenum = int(pagenum) if int(pagenum) <= p.num_pages else p.num_pages
    else:
        pagenum = 1
    context = {
        "view": "list",
        "title": "Stratigraphic Units",
        "newitemlink": "/su/new/",
        "count": p.count,
        "pages": p.get_elided_page_range(pagenum, on_each_side=2, on_ends=1),  # type: ignore
        "all_items": p.page(pagenum),
        "params": paramstring,
        "form": SUFilters(initial=params),
    }
    return render(
        request,
        "contexts/sus_list.html",
        context,
    )
