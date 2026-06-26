import re

from django.shortcuts import redirect, render

from ..models import Lot
from ..forms import LotForm


def _detail_view(request, id, model, form):
    context = {}
    instance = None
    newrecordid = None
    if not request.path.endswith("/new/"):
        instance = model.objects.filter(id=id).first()
    editable = False
    if str(request.user) != "AnonymousUser":
        editable = True
    if request.method == "POST":
        form = form(request.POST, instance=instance, editable=editable)
        if form.is_valid():
            new_record = form.save()
            context = {
                "title": f"{model.__name__} Saved",
                "form": form,
            }
            if new_record.pk != id:  # a new record was created
                newrecordid = new_record.pk
        else:
            for eacherror in form.non_field_errors():
                form.add_error(
                    re.match("This (.*) already", eacherror).group(1),
                    eacherror,
                )
            context = {
                "title": f"{model.__name__} Not Saved",
                "form": form,
            }
    else:
        context["form"] = form(instance=instance, editable=editable, user=request.user)
        if request.path.endswith("/new/"):
            context["title"] = f"New {model.__name__}"
        else:
            context["title"] = f"{model.__name__} Details"
    return newrecordid, context


def lot_detail(request, id=None):
    newpk, context = _detail_view(request, id, Lot, LotForm)
    if newpk:
        return redirect(f"/lot/{newpk}/")
    context["newitemlink"] = "/lot/new/"
    return render(
        request,
        "contexts/details.html",
        context,
    )
