from django.urls import path

from . import views


urlpatterns = [
    path("locales/<str:contexttype>/", views.locales_list),
    path("locales/<str:contexttype>/export/", views.locales_list_export),
    path("locale/new/", views.locale_detail),
    path("locale/<int:id>/", views.locale_detail),
    path("stratigraphic_units/", views.sus_list),
    path("stratigraphic_units/export/", views.sus_list_export),
    path("su/new/", views.su_detail),
    path("su/<int:id>/", views.su_detail),
    path("lots/", views.lots_list),
    path("lots/export/", views.lots_list_export),
    path("lot/new/", views.lot_detail),
    path("lot/<int:id>/", views.lot_detail),
    path("<str:contexttype>/", views.simple_list),
    path("<str:contexttype>/export/", views.simple_list_export),
]
