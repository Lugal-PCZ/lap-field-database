import re

from django.shortcuts import redirect, render


def mainmenu(request):
    return render(
        request,
        "main_menu.html",
        {"title": "Main Menu"},
    )


def lap_form_handler(request, model, form, id):
    context = {"newitemlink": f"/{model.__name__.lower()}/new/"}
    context["title"] = f"{model.__name__} Details"
    if request.path.endswith("/new/"):
        context["title"] = f"New {model.__name__}"
    instance = None
    if not request.path.endswith("/new/"):
        instance = model.objects.filter(id=id).first()
    editable = False
    if str(request.user) != "AnonymousUser":
        editable = True
    context["form"] = form(instance=instance, editable=editable, user=request.user)
    if request.method == "POST":
        form = form(request.POST, request.FILES, instance=instance, editable=editable, user=request.user)
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
