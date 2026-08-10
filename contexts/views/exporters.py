import codecs, csv, io, os, shutil
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from django.conf import settings
from django.http import HttpResponse
from django.db.models import F, Prefetch
from django.template.loader import render_to_string

from xhtml2pdf import pisa

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


def locale_details_export(request, id):
    details = (
        Locale.objects.filter(id=id).prefetch_related(
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
    ).first()
    seasons = []
    seasons_list = set()
    for each_su in details.sus_list:  # type: ignore
        seasons.append(each_su.seasons.values()[0]["id"])
        seasons_list.add(each_su.seasons.values()[0]["name"])
    seasons_list = list(seasons_list)
    seasons_list.sort()
    details.seasons = seasons  # type: ignore
    details.seasons_list = seasons_list  # type: ignore
    sus = []
    for each_su in details.sus_list:  # type: ignore
        sus.append(str(each_su))
    details.sus_list = sus  # type: ignore
    with open(Path(settings.BASE_DIR / "static/pdfs.css"), "r") as f:
        pdf_css = f.read()
    context = {
        "pdf_css": pdf_css,
        "formatted_name": details.formatted_name(),  # type: ignore
        "locale": details,
    }
    template = render_to_string("contexts/locale_pdf.html", context)
    result = io.BytesIO()
    pisa.pisaDocument(io.BytesIO(template.encode("UTF-8")), result)
    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="LAP Locale {details.formatted_name()}.pdf"'  # type: ignore
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


def su_details_export(request, id):
    details = (
        SU.objects.filter(id=id).prefetch_related(
            Prefetch(
                "seasons",
                queryset=Season.objects.all(),
                to_attr="seasons_list",
            )
        )
    ).first()
    seasons = []
    for each_season in details.seasons_list:  # type: ignore
        seasons.append(str(each_season))
    details.seasons_list = seasons  # type: ignore
    lots = []
    for each_lot in details.lot_set.values():  # type: ignore
        lots.append(each_lot["number"])
    lots.sort()
    with open(Path(settings.BASE_DIR / "static/pdfs.css"), "r") as f:
        pdf_css = f.read()
    context = {
        "pdf_css": pdf_css,
        "su": details,
        "lots": lots,
        "filename": str(details.tracing).split("/")[-1],  # type: ignore
    }
    template = render_to_string("contexts/su_pdf.html", context)
    result = io.BytesIO()
    pisa.pisaDocument(io.BytesIO(template.encode("UTF-8")), result)
    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="LAP SU {details}.pdf"'  # type: ignore
    return response


def su_tracing_export(request, id):
    record = SU.objects.filter(id=id)[0]
    name = record.tracingexportname()
    worldfile = str(record.worldfile_contents)
    if os.path.exists(f"/tmp/{name}.zip"):
        os.remove(f"/tmp/{name}.zip")
    shutil.rmtree(f"/tmp/{name}/", ignore_errors=True)
    os.makedirs(f"/tmp/{name}")
    shutil.copy(str(record.tracing), f"/tmp/{name}/{name}.jpg")
    with open(f"/tmp/{name}/{name}.jgw", "w") as f:
        f.write(worldfile)
    with ZipFile(f"/tmp/{name}.zip", "w", compression=ZIP_DEFLATED) as f:
        f.write(f"/tmp/{name}/{name}.jpg", arcname=f"{name}/{name}.jpg")
        f.write(f"/tmp/{name}/{name}.jgw", arcname=f"{name}/{name}.jgw")
    with open(f"/tmp/{name}.zip", "rb") as f:
        response = HttpResponse(
            f.read(),
            headers={
                "Content-Type": "application/zip",
                "Content-Disposition": f'attachment; filename="{name}.zip"',
            },
        )
    return response
