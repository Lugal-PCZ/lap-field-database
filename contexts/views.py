from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import render

from .filters import SUFilters, LocaleFilters, LotFilters
from .forms import LocaleForm, LotForm, SUForm
from .models import Area, Locale, Lot, Season, SU


# List views start here

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
    all_items = Locale.objects.filter(method=method)
    params, paramstring = _build_params(request, ["area"])
    if area := params["area"]:
        all_items = all_items.filter(area_id=area)
    p = Paginator(all_items, ITEMSPERPAGE)
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
    all_items = SU.objects.all().prefetch_related(
        Prefetch(
            "seasons",
            Season.objects.all(),
            to_attr="season_list",
        )
    )
    params, paramstring = _build_params(request, ["locale", "type", "season"])
    if locale := params["locale"]:
        all_items = all_items.filter(locale_id=locale)
    if type := params["type"]:
        all_items = all_items.filter(prefix_id=type)
    if season := params["season"]:
        all_items = all_items.filter(seasons__id=season)
    p = Paginator(all_items, ITEMSPERPAGE)
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
    all_items = Lot.objects.all()
    params, paramstring = _build_params(
        request,
        ["su", "locale", "contents", "season"],
    )
    if su := request.GET.get("su"):
        all_items = all_items.filter(su_id=su)
    if locale := request.GET.get("locale"):
        all_items = all_items.filter(su__locale_id=locale)
    if contents := request.GET.get("contents"):
        if contents == "None":
            all_items = all_items.filter(contents__isnull=True)
        else:
            all_items = all_items.filter(contents__iexact=contents)
    if season := request.GET.get("season"):
        all_items = all_items.filter(season_id=season)
    p = Paginator(all_items, ITEMSPERPAGE)
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


# Detail views start here


def locale_detail(request, id=None):
    context = {}
    locale = None
    if not request.path.endswith("/new/"):
        locale = Locale.objects.filter(id=id).first()
    editable = False
    if str(request.user) != "AnonymousUser":
        editable = True
    if request.method == "POST":
        form = LocaleForm(request.POST, instance=locale, editable=editable)
        if form.is_valid():
            form.save()
            context = {
                "title": "Locale Saved",
                "form": form,
            }
        else:
            context = {
                "title": "Locale Not Saved",
                "form": form,
            }
    else:
        context["form"] = LocaleForm(instance=locale, editable=editable)
        if request.path.endswith("/new/"):
            context["title"] = "New Locale"
        else:
            context["title"] = "Locale Details"
def locale_detail(request, id=None):
    context = _detail_view(request, id, Locale, LocaleForm)
    context["newitemlink"] = "/locale/new/"
    return render(
        request,
        "contexts/detail.html",
        context,
    )


def su_detail(request, id=None):
    context = _detail_view(request, id, SU, SUForm)
    context["newitemlink"] = "/su/new/"
    return render(
        request,
        "contexts/detail.html",
        context,
    )


def lot_detail(request, id=None):
    context = _detail_view(request, id, Lot, LotForm)
    context["newitemlink"] = "/lot/new/"
    return render(
        request,
        "contexts/detail.html",
        context,
    )
