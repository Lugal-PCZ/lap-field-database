import codecs, csv, re

from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import F, Prefetch
from django.shortcuts import redirect, render

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


def simple_list_export(request, contexttype):
    if contexttype == "seasons":
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="LAP Seasons.csv"'},
        )
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow(
            [
                "Year",
                "Time of Year",
                "Name",
            ]
        )
        for record in Season.objects.all():
            writer.writerow(
                [
                    record.year,
                    record.timeofyear,
                    record.name,
                ]
            )
    elif contexttype == "areas":
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="LAP Areas.csv"'},
        )
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow(
            [
                "Name",
                "Short Name",
            ]
        )
        for record in Area.objects.all():
            writer.writerow(
                [
                    record,
                    record.shortname,
                ]
            )
    return response


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
    all_items = Locale.objects.filter(method=method).order_by(F("name")[0:6])
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


def locales_list_export(request, contexttype):
    if contexttype == "excavation_trenches":
        headers = {"Content-Disposition": 'attachment; filename="LAP Excavation Trenches.csv"'}
        method = "Excavation"
    elif contexttype == "scraping_trenches":
        headers = {"Content-Disposition": 'attachment; filename="LAP Scraping Trenches.csv"'}
        method = "Scraping"
    elif contexttype == "survey_units":
        headers = {"Content-Disposition": 'attachment; filename="LAP Survey Units.csv"'}
        method = "Survey"
    elif contexttype == "surface_findspots":
        headers = {"Content-Disposition": 'attachment; filename="LAP Surface Findspots.csv"'}
        method = "Surface Find"
    all_items = Locale.objects.filter(method=method).order_by(F("name")[0:6])
    params, paramstring = _build_params(request, ["area"])
    if area := params["area"]:
        all_items = all_items.filter(area_id=area)
    response = HttpResponse(
        content_type="text/csv",
        headers=headers,
    )
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response)
    writer.writerow(
        [
            "Name",
            "Area",
            "Method",
            "Notes",
        ]
    )
    for record in all_items:
        writer.writerow(
            [
                record,
                record.area,
                record.method,
                record.notes,
            ]
        )
    return response


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


def sus_list_export(request):
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
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="LAP Stratigraphic Units.csv"'},
    )
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response)
    writer.writerow(
        [
            "SU or 1LAP/3LAP Locus",
            "Locale",
            "Date Assigned",
            "Recorded By",
            "Season(s)",
            "Feature Type",
            "Architectural Features",
            "Architectural Technique",
            "Elevation (top)",
            "Elevation (bottom)",
            "Dimensions",
            "Color",
            "Composition",
            "Texture",
            "Inclusions",
            "Same As",
            "Abuts",
            "Covered By",
            "Covers",
            "Cut By",
            "Cuts",
            "Filled By",
            "Fills",
            "Description",
            "Interpretation",
            "Photos",
            "Photogrammetry Numbers",
            "Voided",
        ]
    )
    for record in all_items:
        seasons = []
        for each_season in record.season_list:
            seasons.append(str(each_season))
        voided = ""
        if record.voided:
            voided = "True"
        writer.writerow(
            [
                record,
                record.locale,
                record.dateassigned,
                record.recordedby,
                ", ".join(seasons),
                record.prefix,
                record.architecturalfeatures,
                record.architecturaltechnique,
                record.elevationtop,
                record.elevationbottom,
                record.dimensions,
                record.color,
                record.composition,
                record.texture,
                record.inclusions,
                record.sameas,
                record.abuts,
                record.coveredby,
                record.covers,
                record.cutby,
                record.cuts,
                record.filledby,
                record.fills,
                record.description,
                record.interpretation,
                record.photos,
                record.photogrammetrynumbers,
                voided,
            ]
        )
    return response


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


def lots_list_export(request):
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
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="LAP Lots.csv"'},
    )
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response)
    writer.writerow(
        [
            "Lot",
            "SU or 1LAP/3LAP Locus",
            "Locale",
            "Contents",
            "Date Assigned",
            "Season",
            "Notes",
            "Voided",
        ]
    )
    for record in all_items:
        contents = record.contents
        if not record.contents:
            contents = "-"
        voided = ""
        if record.voided:
            voided = "True"
        writer.writerow(
            [
                record,
                record.su,
                record.su.locale,
                record.contents,
                record.dateassigned,
                record.season,
                record.notes,
                voided,
            ]
        )
    return response


# Detail views start here


def _detail_view(request, id, model, form):
    context = {}
    instance = None
    newrecordid = None
    if not request.path.endswith("/new/"):
        instance = model.objects.filter(id=id).first()
    editable = False
    if str(request.user) != "AnonymousUser":
        editable = True
    if request.method == "POST":
        form = form(request.POST, instance=instance, editable=editable)
        if form.is_valid():
            new_record = form.save()
            context = {
                "title": f"{model.__name__} Saved",
                "form": form,
            }
            if new_record.pk != id:  # a new record was created
                newrecordid = new_record.pk
        else:
            for eacherror in form.non_field_errors():
                form.add_error(
                    re.match("This (.*) already", eacherror).group(1),
                    eacherror,
                )
            context = {
                "title": f"{model.__name__} Not Saved",
                "form": form,
            }
    else:
        context["form"] = form(instance=instance, editable=editable)
        if request.path.endswith("/new/"):
            context["title"] = f"New {model.__name__}"
        else:
            context["title"] = f"{model.__name__} Details"
    return newrecordid, context


def locale_detail(request, id=None):
    newpk, context = _detail_view(request, id, Locale, LocaleForm)
    if newpk:
        messages.info(request, "New Locale Created")
        return redirect(f"/locale/{newpk}/")
    context["newitemlink"] = "/locale/new/"
    return render(
        request,
        "contexts/detail.html",
        context,
    )


def su_detail(request, id=None):
    newpk, context = _detail_view(request, id, SU, SUForm)
    if newpk:
        return redirect(f"/su/{newpk}/")
    context["newitemlink"] = "/su/new/"
    return render(
        request,
        "contexts/detail.html",
        context,
    )


def lot_detail(request, id=None):
    newpk, context = _detail_view(request, id, Lot, LotForm)
    if newpk:
        return redirect(f"/lot/{newpk}/")
    context["newitemlink"] = "/lot/new/"
    return render(
        request,
        "contexts/detail.html",
        context,
    )
