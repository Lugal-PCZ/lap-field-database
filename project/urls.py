from django.urls import path

from .views import exporters, lists


urlpatterns = [
    path("seasons/", lists.seasons_list),
    path("seasons/export/", exporters.seasons_list_export),
    path("areas/", lists.areas_list),
    path("areas/export/", exporters.areas_list_export),
]
