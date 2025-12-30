from django.urls import path
from . import views

urlpatterns = [
    path("human_remains/", views.index, name="index"),
]
