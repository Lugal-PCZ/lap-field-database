import codecs, csv, io
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string

from xhtml2pdf import pisa

from ..models import Sample


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


def samples_list_export(request):
    unfiltered_items = Sample.objects.all()
    params, paramstring = _build_params(request, ["locale", "type", "season"])
    filtered_items = unfiltered_items
    if locale := params["locale"]:
        filtered_items = [item for item in filtered_items if item.lot.su.locale_id == int(locale)]  # type: ignore
    if sampletype := params["type"]:
        filtered_items = [item for item in filtered_items if item.sampletype_id == int(sampletype)]  # type: ignore
    if season := params["season"]:
        filtered_items = [item for item in filtered_items if item.season_id == int(season)]  # type: ignore
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="LAP Samples.csv"'},
    )
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response)
    writer.writerow(
        [
            "Sample",
            "Season",
            "Excavation Number",
            "Area",
            "Locale",
            "Method",
            "SU or 1LAP/3LAP Locus",
            "Lot",
            "Excavation Date",
            "Registration Date",
            "Registrar",
            "Type",
            "Box",
            "Intended Analysis",
            "Notes",
            "Voided",
        ]
    )
    for record in filtered_items:
        voided = ""
        if record.voided:
            voided = "VOID"
        writer.writerow(
            [
                record.number,
                record.season,
                record.excavationnumber,
                record.lot.su.locale.area,
                record.lot.su.locale,
                record.lot.su.locale.method,
                record.lot.su,
                record.lot,
                record.excavationdate,
                record.registrationdate,
                record.registrar,
                record.sampletype,
                record.box,
                record.intendedanalysis,
                record.notes,
                voided,
            ]
        )
    return response


def sample_details_export(request, id):
    details = Sample.objects.filter(id=id).first()
    with open(Path(settings.BASE_DIR / "static/pdfs.css"), "r") as f:
        pdf_css = f.read()
    context = {
        "pdf_css": pdf_css,
        "sample": details,
    }
    template = render_to_string("samples/sample_pdf.html", context)
    result = io.BytesIO()
    pisa.pisaDocument(io.BytesIO(template.encode("UTF-8")), result)
    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="LAP Sample {details.number}.pdf"'  # type: ignore
    return response
