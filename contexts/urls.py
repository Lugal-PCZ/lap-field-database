from django.urls import path

from .views import details, exporters, lists


urlpatterns = [
    path("locales/<str:contexttype>/", lists.locales_list),
    path("locales/<str:contexttype>/export/", exporters.locales_list_export),
    path("locale/new/", details.locale_detail),
    path("locale/<int:id>/", details.locale_detail),
    path("sus/", lists.sus_list),
    path("sus/export/", exporters.sus_list_export),
    path("su/new/", details.su_detail),
    path("su/<int:id>/", details.su_detail),
]
