import codecs, csv

from django.http import HttpResponse
from django.db.models import F, Prefetch

from ..models import Area, Locale, Lot, Season, SU


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
    # all_items = Locale.objects.filter(method=method).order_by(F("name")[0:6])
    all_items = (
        Locale.objects.prefetch_related(
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
        .filter(method=method)
        .order_by(F("name")[0:6], "id")
    )
    params, paramstring = _build_params(request, ["area"])
    if area := params["area"]:
        all_items = all_items.filter(area_id=area)
    for each_item in all_items:
        seasons = set()
        for each_su in each_item.sus_list:
            seasons.add(each_su.seasons.values_list()[0][1])
        seasons = list(seasons)
        seasons.sort()
        each_item.seasons_list = seasons
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
            "Season(s)",
            "Notes",
        ]
    )
    for record in all_items:
        writer.writerow(
            [
                record,
                record.area,
                record.method,
                ", ".join(record.seasons_list),  # type: ignore
                record.notes,
            ]
        )
    return response


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
            "SU or 1/3LAP Locus",
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
            voided = "VOID"
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
            "SU or 1/3LAP Locus",
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
            voided = "VOID"
        writer.writerow(
            [
                record,
                record.su,
                record.su.locale,
                contents,
                record.dateassigned,
                record.season,
                record.notes,
                voided,
            ]
        )
    return response
