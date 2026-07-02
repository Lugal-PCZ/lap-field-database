import re

from django.contrib import messages
from django.shortcuts import redirect, render


def mainmenu(request):
    return render(
        request,
        "main_menu.html",
        {"title": "Main Menu"},
    )
