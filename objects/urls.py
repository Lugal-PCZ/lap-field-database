from django.urls import path

from .views import lists
# from .views import ajax, details, exporters, lists


urlpatterns = [
    path("objects/", lists.objects_list),
    # path("objects/export/", exporters.objects_list_export),
    # path("object/new/", details.object_details),
    # path("object/<int:id>/", details.object_details),
    # path("object/<int:id>/export/", exporters.object_details_export),
    # path("ajax/load_locale/", ajax.load_locale),
]
