from django.core.paginator import Paginator
from django.db.models import F, Prefetch
from django.shortcuts import render

from ..forms import SUFilters, LocaleFilters, LotFilters
from ..models import Area, Locale, Lot, Season, SU


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


def simple_list(request, contexttype):
    title = ""
    all_items = []
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
    unfiltered_items = (
        Locale.objects.filter(method=method)
        .order_by(F("name")[0:6], "id")  # type: ignore
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
            print(each_item.seasons)  # type: ignore
            if int(season) in each_item.seasons:  # type: ignore
                refiltered_items.append(each_item)
        filtered_items = refiltered_items
    p = Paginator(filtered_items, ITEMSPERPAGE)
    if pagenum := request.GET.get("p"):
        pagenum = int(pagenum) if int(pagenum) <= p.num_pages else p.num_pages
    else:
        pagenum = 1
    context = {
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


def lots_list(request):
    unfiltered_items = Lot.objects.all()
    params, paramstring = _build_params(request, ["su", "locale", "contents", "season"])
    filtered_items = unfiltered_items
    if su := params["su"]:
        filtered_items = [item for item in filtered_items if item.su_id == int(su)]  # type: ignore
    if locale := params["locale"]:
        filtered_items = [item for item in filtered_items if item.su.locale_id == int(locale)]  # type: ignore
    if contents := params["contents"]:
        if contents == "None":
            filtered_items = [item for item in filtered_items if item.contents == None]
        else:
            filtered_items = [item for item in filtered_items if str(item.contents).upper() == contents.upper()]
    if season := params["season"]:
        filtered_items = [item for item in filtered_items if item.season.id == int(season)]  # type: ignore
    p = Paginator(filtered_items, ITEMSPERPAGE)
    if pagenum := request.GET.get("p"):
        pagenum = int(pagenum) if int(pagenum) <= p.num_pages else p.num_pages
    else:
        pagenum = 1
    context = {
        "title": "Lots",
        "newitemlink": "/lot/new/",
        "count": p.count,
        "pages": p.get_elided_page_range(pagenum, on_each_side=2, on_ends=1),  # type: ignore
        "all_items": p.page(pagenum),
        "params": paramstring,
        "form": LotFilters(initial=params),
    }
    return render(
        request,
        "contexts/lots_list.html",
        context,
    )
