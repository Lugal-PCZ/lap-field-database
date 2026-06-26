import codecs, csv

from django.http import HttpResponse

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
