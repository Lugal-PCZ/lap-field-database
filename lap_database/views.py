from django.shortcuts import render


def mainmenu(request):
    return render(
        request,
        "menu.html",
        {"title": "Main Menu"},
    )
