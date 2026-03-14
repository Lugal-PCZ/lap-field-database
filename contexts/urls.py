from django.urls import path

from . import views

urlpatterns = [
    path("locales/<str:contexttype>/", views.locales_list),
    path("stratigraphic_units/", views.sus_list),
    path("lots/", views.lots_list),
    path("<str:contexttype>/", views.simple_list),
]
