from django.shortcuts import render

from ..models import Area, Season


ITEMSPERPAGE = 100


def simple_list(request, contexttype):
    title = ""
    all_items = []
    if contexttype == "seasons":
        title = Season._meta.verbose_name_plural
        all_items = Season.objects.all()
    elif contexttype == "areas":
        title = Area._meta.verbose_name_plural
        all_items = Area.objects.all()
    context = {
        "title": title,
        "count": len(all_items),
        "all_items": all_items,
    }
    return render(
        request,
        "contexts/simple_list.html",
        context,
    )
