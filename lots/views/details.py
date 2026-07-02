import re

from django.shortcuts import redirect, render

from ..models import Lot
from ..forms import LotForm


def lot_detail(request, id=None):
    context = {"newitemlink": "/lot/new/"}
    context["title"] = "Lot Details"
    if request.path.endswith("/new/"):
        context["title"] = "New Lot"
    instance = None
    if not request.path.endswith("/new/"):
        instance = Lot.objects.filter(id=id).first()
    editable = False
    if str(request.user) != "AnonymousUser":
        editable = True
    context["form"] = LotForm(instance=instance, editable=editable, user=request.user)  # type: ignore
    if request.method == "POST":
        form = LotForm(request.POST, request.FILES, instance=instance, editable=editable, user=request.user)
        if form.is_valid():
            record = form.save()
            if record.pk == id:  # a record was updated
                return redirect(request.path)
            if record.pk != id:  # a new record was created
                id = record.pk
                return redirect(request.path.replace("/new/", f"/{record.pk}/"))
        else:
            for eacherror in form.non_field_errors():
                form.add_error(
                    re.match("This (.*) already", eacherror).group(1),  # type: ignore
                    eacherror,
                )
            context["form"] = form  # type: ignore
            return render(request, "details.html", context)
    return render(request, "details.html", context)
