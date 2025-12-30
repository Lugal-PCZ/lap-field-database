from django.db.models import IntegerField
from django.db.models.functions import Substr
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from .models import Area, Locale, Lot, Season, SU, SUPrefix


def index(request):
    template = loader.get_template("contexts/index.html")
    return HttpResponse(template.render())


def list_all(request, contexttype):
    if contexttype == "areas":
        all_items = Area.objects.all()
        title = Area._meta.verbose_name_plural
    elif contexttype == "seasons":
        all_items = Season.objects.all()
        title = Season._meta.verbose_name_plural
    elif contexttype == "trenches":
        all_items = Locale.objects.filter(
            method__in=["Excavation", "Scraping"]
        ).order_by(Substr("name", 1, 7))
        title = "Trenches"
    elif contexttype == "surveyunits":
        all_items = Locale.objects.filter(method="Survey")
        title = "Survey Units"
    elif contexttype == "surfacefindspots":
        all_items = Locale.objects.filter(method="Surface Find").order_by(
            "area", "name"
        )
        title = "Surface Findspots"

    context = {
        "all_items": all_items,
        "title": title,
    }
    return render(request, "contexts/list.html", context)
