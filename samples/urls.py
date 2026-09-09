from django.urls import path

from .views import ajax, details, exporters, lists


urlpatterns = [
    path("samples/", lists.samples_list),
    path("samples/export/", exporters.samples_list_export),
    path("sample/new/", details.sample_details),
    path("sample/<int:id>/", details.sample_details),
    path("sample/<int:id>/export/", exporters.sample_details_export),
    path("sample/ajax/load_nextnumber/", ajax.load_nextnumber),
    path("sample/ajax/load_su/", ajax.load_su),
    path("sample/ajax/load_locale/", ajax.load_locale),
]
