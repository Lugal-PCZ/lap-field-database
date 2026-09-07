import codecs, csv, io
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string

from xhtml2pdf import pisa

from ..models import Lot


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


def lots_list_export(request):
    unfiltered_items = Lot.objects.all()
    params, paramstring = _build_params(request, ["locale", "su", "contents", "season"])
    filtered_items = unfiltered_items
    if locale := params["locale"]:
        filtered_items = [item for item in filtered_items if item.su.locale_id == int(locale)]  # type: ignore
    if su := params["su"]:
        filtered_items = [item for item in filtered_items if item.su_id == int(su)]  # type: ignore
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
            "Area",
            "Locale",
            "SU or 1LAP/3LAP Locus",
            "Contents",
            "Date Assigned",
            "Season",
            "Notes",
            "Objects",
            "Voided",
        ]
    )
    for record in filtered_items:
        contents = record.contents
        if not record.contents:
            contents = "-"
        objects = []
        for each_object in record.object_set.values():  # type: ignore
            objects.append(each_object["number"])
        voided = ""
        if record.voided:
            voided = "VOID"
        writer.writerow(
            [
                record,
                record.su.locale.area,
                record.su.locale,
                record.su,
                contents,
                record.dateassigned,
                record.season,
                record.notes,
                ", ".join(objects),
                voided,
            ]
        )
    return response


def lot_details_export(request, id):
    details = Lot.objects.filter(id=id).first()
    objects = []
    for each_object in details.object_set.values():  # type: ignore
        objects.append(each_object["number"])
    objects.sort()
    with open(Path(settings.BASE_DIR / "static/pdfs.css"), "r") as f:
        pdf_css = f.read()
    context = {
        "pdf_css": pdf_css,
        "lot": details,
        "objects": objects,
    }
    template = render_to_string("lots/lot_pdf.html", context)
    result = io.BytesIO()
    pisa.pisaDocument(io.BytesIO(template.encode("UTF-8")), result)
    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="LAP Lot {details.number}.pdf"'  # type: ignore
    return response
