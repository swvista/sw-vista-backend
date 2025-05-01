from django.urls import path

from . import views

urlpatterns = [
    path("venue/", views.venue, name="venue"),
    path("venue/<int:id>/", views.get_venue_by_id, name="get_venue_by_id"),
]
