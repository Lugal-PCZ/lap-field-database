from django.urls import path

from . import views


urlpatterns = [
    path("locales/<str:contexttype>/", views.locales_list),
    path("locale/new/", views.locale_detail),
    path("locale/<int:id>/", views.locale_detail),
    path("stratigraphic_units/", views.sus_list),
    path("su/new/", views.su_detail),
    path("su/<int:id>/", views.su_detail),
    path("lots/", views.lots_list),
    path("lot/new/", views.lot_detail),
    path("lot/<int:id>/", views.lot_detail),
    path("<str:contexttype>/", views.simple_list),
]
