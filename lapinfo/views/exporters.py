import codecs, csv, io
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string

from xhtml2pdf import pisa

from ..models import Area, Season


def seasons_list_export(request):
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
    return response


def areas_list_export(request):
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


def area_details_export(request, id):
    details = Area.objects.filter(id=id).first()
    locales_list = []
    for each_locale in details.locales.values():
        locales_list.append(each_locale["name"])
    locales_list.sort()
    details.locales_list = "; ".join(locales_list)  # type: ignore
    with open(Path(settings.BASE_DIR / "static/pdfs.css"), "r") as f:
        pdf_css = f.read()
    context = {
        "pdf_css": pdf_css,
        "formatted_name": details.formatted_name(),  # type: ignore
        "area": details,
    }
    template = render_to_string("lapinfo/area_pdf.html", context)
    result = io.BytesIO()
    pisa.pisaDocument(io.BytesIO(template.encode("UTF-8")), result)
    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="LAP Area {details.formatted_name().removeprefix("Area ")}.pdf"'  # type: ignore
    )
    return response
