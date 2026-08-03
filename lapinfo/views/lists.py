from django.shortcuts import render

from ..models import Area, Season


ITEMSPERPAGE = 100


def seasons_list(request):
    title = Season._meta.verbose_name_plural
    all_items = Season.objects.all()
    context = {
        "view": "list",
        "title": title,
        "count": len(all_items),
        "all_items": all_items,
    }
    return render(
        request,
        "lapinfo/info_list.html",
        context,
    )


def areas_list(request):
    title = Area._meta.verbose_name_plural
    all_items = Area.objects.all()
    context = {
        "view": "list",
        "title": title,
        "count": len(all_items),
        "all_items": all_items,
    }
    return render(
        request,
        "lapinfo/info_list.html",
        context,
    )
