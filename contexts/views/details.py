import re

from django.shortcuts import redirect, render

from ..models import Locale, SU
from ..forms import LocaleForm, SUForm


def locale_detail(request, id=None):
    context = {"newitemlink": "/locale/new/"}
    context["title"] = "Locale Details"
    if request.path.endswith("/new/"):
        context["title"] = "New Locale"
    instance = None
    if not request.path.endswith("/new/"):
        instance = Locale.objects.filter(id=id).first()
    editable = False
    if str(request.user) != "AnonymousUser":
        editable = True
    context["form"] = LocaleForm(instance=instance, editable=editable, user=request.user)  # type: ignore
    if request.method == "POST":
        form = LocaleForm(request.POST, request.FILES, instance=instance, editable=editable, user=request.user)
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


def su_detail(request, id=None):
    context = {"newitemlink": "/stratigraphic_unit/new/"}
    context["title"] = "SU Details"
    if request.path.endswith("/new/"):
        context["title"] = "New SU"
    instance = None
    if not request.path.endswith("/new/"):
        instance = SU.objects.filter(id=id).first()
    editable = False
    if str(request.user) != "AnonymousUser":
        editable = True
    context["form"] = SUForm(instance=instance, editable=editable, user=request.user)  # type: ignore
    if request.method == "POST":
        form = SUForm(request.POST, request.FILES, instance=instance, editable=editable, user=request.user)
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
