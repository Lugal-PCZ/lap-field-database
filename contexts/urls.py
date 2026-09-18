from django.urls import path

from .views import ajax, details, exporters, lists


urlpatterns = [
    path("locales/<str:contexttype>/", lists.locales_list),
    path("locales/<str:contexttype>/export/", exporters.locales_list_export),
    path("locale/new/", details.locale_details),
    path("locale/<int:id>/", details.locale_details),
    path("locale/<int:id>/export/", exporters.locale_details_export),
    path("sus/", lists.sus_list),
    path("sus/export/", exporters.sus_list_export),
    path("su/new/", details.su_details),
    path("su/<int:id>/", details.su_details),
    path("su/<int:id>/export/", exporters.su_details_export),
    path("su/<int:id>/tracing/", exporters.su_tracing_export),
    path("su/ajax/load_method/", ajax.load_method),
]
