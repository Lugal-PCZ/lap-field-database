from django.core.paginator import Paginator
from django.shortcuts import render

from ..models import Lot
from ..forms import LotFilters


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


def lots_list(request):
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
    p = Paginator(filtered_items, ITEMSPERPAGE)
    if pagenum := request.GET.get("p"):
        pagenum = int(pagenum) if int(pagenum) <= p.num_pages else p.num_pages
    else:
        pagenum = 1
    context = {
        "view": "list",
        "title": "Lots",
        "newitemlink": "/lot/new/",
        "count": p.count,
        "pages": p.get_elided_page_range(pagenum, on_each_side=2, on_ends=1),  # type: ignore
        "all_items": p.page(pagenum),
        "params": paramstring,
        "form": LotFilters(initial=params),
    }
    return render(
        request,
        "lots/list.html",
        context,
    )
