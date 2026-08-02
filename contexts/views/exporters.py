import codecs, csv

from django.http import HttpResponse
from django.db.models import F, Prefetch

from ..models import Locale, SU
from lapinfo.models import Season


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
            if int(season) in each_item.seasons:  # type: ignore
                refiltered_items.append(each_item)
        filtered_items = refiltered_items
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
            "Seasons",
            "SUs",
            "Notes",
        ]
    )
    for record in filtered_items:
        sus = []
        for each_su in record.sus_list:  # type: ignore
            sus.append(str(each_su))
        writer.writerow(
            [
                record,
                record.area,
                record.method,
                ", ".join(record.seasons_list),  # type: ignore
                ", ".join(sus),  # type: ignore
                record.notes,
            ]
        )
    return response


def locale_detail_export(request, id):
    pass


def sus_list_export(request):
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
            "Seasons",
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
            "Lots",
            "Photos",
            "Photogrammetry Numbers",
            "Voided",
        ]
    )
    for record in filtered_items:
        seasons = []
        for each_season in record.seasons_list:  # type: ignore
            seasons.append(str(each_season))
        lots = []
        for each_lot in record.lot_set.values():  # type: ignore
            lots.append(each_lot["number"])
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
                ", ".join(lots),
                record.photos,
                record.photogrammetrynumbers,
                voided,
            ]
        )
    return response


def su_detail_export(request, id):
    pass
