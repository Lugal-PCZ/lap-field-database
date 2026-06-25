from django.urls import path

from .views import ajax, details, exporters, lists


urlpatterns = [
    path("locales/<str:contexttype>/", lists.locales_list),
    path("locales/<str:contexttype>/export/", exporters.locales_list_export),
    path("locale/new/", details.locale_detail),
    path("locale/<int:id>/", details.locale_detail),
    path("stratigraphic_units/", lists.sus_list),
    path("stratigraphic_units/export/", exporters.sus_list_export),
    path("su/new/", details.su_detail),
    path("su/<int:id>/", details.su_detail),
    path("lots/", lists.lots_list),
    path("lots/export/", exporters.lots_list_export),
    path("lot/new/", details.lot_detail),
    path("lot/<int:id>/", details.lot_detail),
    path("ajax/load_locale/", ajax.load_locale),
]
