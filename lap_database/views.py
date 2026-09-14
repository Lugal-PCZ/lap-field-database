import re

from django.shortcuts import redirect, render
from django.contrib import messages


def mainmenu(request):
    return render(
        request,
        "main_menu.html",
        {"title": "Main Menu"},
    )


def lap_form_handler(request, model, form, id, message=None):
    context = {}
    if not model.__name__.lower() == "area":  # This is to prevent users from creating new Areas
        context["newitemlink"] = f"/{model.__name__.lower()}/new/"
    context["view"] = "details"
    context["title"] = f"{model.__name__} Details"
    if request.path.endswith("/new/"):
        context["title"] = f"New {model.__name__}"
        instance = None
    else:
        instance = model.objects.filter(id=id).first()
    editable = False
    if str(request.user) != "AnonymousUser":
        editable = True
    context["form"] = form(instance=instance, editable=editable, user=request.user)
    if request.method == "POST":
        form = form(request.POST, request.FILES, instance=instance, editable=editable, user=request.user)
        if form.is_valid():
            record = form.save()
            if message:
                messages.success(request, message)
            if record.pk == id:  # a record was updated
                return redirect(request.path)
            if record.pk != id:  # a new record was created
                id = record.pk
                return redirect(request.path.replace("/new/", f"/{record.pk}/"))
        else:
            for eacherror in form.non_field_errors():
                if re.match("The (\\w+) given", eacherror):
                    thefield = re.match("The (\\w+) given", eacherror).group(1)  # type: ignore
                elif re.match("This (\\w+) already", eacherror):
                    thefield = re.match("This (\\w+) already", eacherror).group(1)  # type: ignore
                form.add_error(
                    thefield,
                    eacherror,
                )
            context["form"] = form  # type: ignore
            return render(request, "details.html", context)
    return render(request, "details.html", context)
