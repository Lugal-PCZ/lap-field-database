import codecs, csv

from django.http import HttpResponse

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
