from django.core.paginator import Paginator
from django.shortcuts import render

from ..models import Object
from ..forms import ObjectFilters


ITEMSPERPAGE = 50


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


def objects_list(request):
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
    p = Paginator(filtered_items, ITEMSPERPAGE)
    if pagenum := request.GET.get("p"):
        pagenum = int(pagenum) if int(pagenum) <= p.num_pages else p.num_pages
    else:
        pagenum = 1
    context = {
        "view": "list",
        "title": "Objects",
        "newitemlink": "/object/new/",
        "count": p.count,
        "pages": p.get_elided_page_range(pagenum, on_each_side=2, on_ends=1),  # type: ignore
        "all_items": p.page(pagenum),
        "params": paramstring,
        "form": ObjectFilters(initial=params),
    }
    return render(
        request,
        "objects/objects_list.html",
        context,
    )
