from django.urls import path
from . import views

urlpatterns = [
    path("pottery/", views.index, name="index"),
]
