from django.urls import path

from .views import ajax, details, exporters, lists


urlpatterns = [
    path("objects/", lists.objects_list),
    path("objects/export/", exporters.objects_list_export),
    path("object/new/", details.object_details),
    path("object/<int:id>/", details.object_details),
    path("object/<int:id>/export/", exporters.object_details_export),
    path("object/ajax/load_objectsubtypes/", ajax.load_objectsubtypes),
    path("object/ajax/load_nextnumber/", ajax.load_nextnumber),
    path("object/ajax/load_su/", ajax.load_su),
    path("object/ajax/load_locale/", ajax.load_locale),
]
