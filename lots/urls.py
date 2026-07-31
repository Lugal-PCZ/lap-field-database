from django.urls import path

from .views import ajax, details, exporters, lists


urlpatterns = [
    path("lots/", lists.lots_list),
    path("lots/export/", exporters.lots_list_export),
    path("lot/new/", details.lot_detail),
    path("lot/<int:id>/", details.lot_detail),
    path("lot/<int:id>/export", exporters.lot_detail_export),
    path("ajax/load_locale/", ajax.load_locale),
]
