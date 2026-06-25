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
                "Name",
                "Year",
                "Time of Year",
            ]
        )
        for record in Season.objects.all():
            writer.writerow(
                [
                    record.name,
                    record.year,
                    record.timeofyear,
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
        # print(record.lot_set.values())
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


def lots_list_export(request):
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
    for record in filtered_items:
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
