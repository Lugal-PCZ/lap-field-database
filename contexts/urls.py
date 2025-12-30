from django.urls import path

from . import views

urlpatterns = [
    path("contexts/", views.index),
    path("<str:contexttype>/", views.list_all),
]
