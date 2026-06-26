from django.shortcuts import render


def mainmenu(request):
    return render(
        request,
        "main_menu.html",
        {"title": "Main Menu"},
    )
