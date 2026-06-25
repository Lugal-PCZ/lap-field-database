from django.urls import path

from .views import exporters, lists


urlpatterns = [
    path("<str:contexttype>/", lists.simple_list),
    path("<str:contexttype>/export/", exporters.simple_list_export),
]
