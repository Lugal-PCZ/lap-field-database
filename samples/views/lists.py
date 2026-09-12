from django.core.paginator import Paginator
from django.shortcuts import render

from ..models import Sample
from ..forms import SampleFilters


ITEMSPERPAGE = 100


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


def samples_list(request):
    unfiltered_items = Sample.objects.all()
    params, paramstring = _build_params(request, ["locale", "type", "season"])
    filtered_items = unfiltered_items
    if locale := params["locale"]:
        filtered_items = [item for item in filtered_items if item.lot.su.locale_id == int(locale)]  # type: ignore
    if sampletype := params["type"]:
        filtered_items = [item for item in filtered_items if item.sampletype_id == int(sampletype)]  # type: ignore
    if season := params["season"]:
        filtered_items = [item for item in filtered_items if item.season_id == int(season)]  # type: ignore
    ids_list = [item.id for item in filtered_items]
    p = Paginator(filtered_items, ITEMSPERPAGE)
    if pagenum := request.GET.get("p"):
        pagenum = int(pagenum) if int(pagenum) <= p.num_pages else p.num_pages
    else:
        pagenum = 1
    context = {
        "view": "list",
        "title": "Samples",
        "newitemlink": "/sample/new/",
        "count": p.count,
        "pages": p.get_elided_page_range(pagenum, on_each_side=2, on_ends=1),  # type: ignore
        "all_items": p.page(pagenum),
        "params": paramstring,
        "form": SampleFilters(initial=params),
        "ids_list": ids_list,
    }
    return render(
        request,
        "samples/samples_list.html",
        context,
    )
