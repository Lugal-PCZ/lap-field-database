import codecs, csv, io
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string

from xhtml2pdf import pisa

from ..models import Object


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


def objects_list_export(request):
    unfiltered_items = Object.objects.all()
    params, paramstring = _build_params(request, ["locale", "type", "material", "season"])
    filtered_items = unfiltered_items
    if locale := params["locale"]:
        filtered_items = [item for item in filtered_items if item.su.locale_id == int(locale)]  # type: ignore
    if objecttype := params["type"]:
        filtered_items = [item for item in filtered_items if item.objecttype_id == int(objecttype)]  # type: ignore
    if material := params["material"]:
        if material == "None":
            filtered_items = [item for item in filtered_items if item.material == None]
        else:
            filtered_items = [item for item in filtered_items if str(item.material).upper() == material.upper()]
    if season := params["season"]:
        filtered_items = [item for item in filtered_items if item.season_id == int(season)]  # type: ignore
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="LAP Objects.csv"'},
    )
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response)
    writer.writerow(
        [
            "Object",
            "Season",
            "Excavation Number",
            "Area",
            "Locale",
            "SU or 1LAP/3LAP Locus",
            "Lot",
            "Excavation Date",
            "Registration Date",
            "Registrar",
            "Type",
            "Subtype",
            "Sealing Function",
            "Clay Slab or Sealing Marking",
            "Blade Serration",
            "Preservation",
            "Repaired/Repurposed",
            "Material",
            "Stone Subtype",
            "Metal Subtype",
            "Main Color",
            "Decoration",
            "Decoration Color",
            "Height",
            "Length",
            "Width",
            "Thickness",
            "Diameter (max)",
            "Diameter (min)",
            "Diameter (holes)",
            "Description",
            "Notes",
            "Sent to Baghdad",
            "Baghdad Number",
            "To Be Photographed",
            "Photographed",
            "To Be Drawn",
            "Drawn",
            "Voided",
        ]
    )
    for record in filtered_items:
        senttobaghdad = "No"
        if record.senttobaghdad:
            senttobaghdad = "Yes"
        tobephotographed = "No"
        if record.tobephotographed:
            tobephotographed = "Yes"
        photographed = "No"
        if record.photographed:
            photographed = "Yes"
        tobedrawn = "No"
        if record.tobedrawn:
            tobedrawn = "Yes"
        drawn = "No"
        if record.drawn:
            drawn = "Yes"
        voided = ""
        if record.voided:
            voided = "VOID"
        writer.writerow(
            [
                record.number,
                record.season,
                record.excavationnumber,
                record.su.locale.area,
                record.su.locale,
                record.su,
                record.lot,
                record.excavationdate,
                record.registrationdate,
                record.registrar,
                record.objecttype,
                record.objectsubtype,
                record.sealingfunction,
                record.clayslaborsealingmarking,
                record.bladeserration,
                record.preservation,
                record.repairedorrepurposed,
                record.material,
                record.stonesubtype,
                record.metalsubtype,
                record.maincolor,
                record.decoration,
                record.decorationcolor,
                record.height,
                record.length,
                record.width,
                record.thickness,
                record.diametermax,
                record.diametermin,
                record.diameterholes,
                record.description,
                record.notes,
                senttobaghdad,
                record.baghdadnumber,
                tobephotographed,
                photographed,
                tobedrawn,
                drawn,
                voided,
            ]
        )
    return response


def object_details_export(request, id):
    details = Object.objects.filter(id=id).first()
    with open(Path(settings.BASE_DIR / "static/pdfs.css"), "r") as f:
        pdf_css = f.read()
    context = {
        "pdf_css": pdf_css,
        "object": details,
        "filename": str(details.image).split("/")[-1],  # type: ignore
    }
    template = render_to_string("objects/object_pdf.html", context)
    result = io.BytesIO()
    pisa.pisaDocument(io.BytesIO(template.encode("UTF-8")), result)
    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="LAP Object {details.number}.pdf"'  # type: ignore
    return response
