from django.urls import path

from . import views

urlpatterns = [
    path("venue/", views.venue, name="venue"),
    path("venue/<int:id>/", views.venue_detail, name="venue_detail"),
]
