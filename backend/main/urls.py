from django.urls import path

from .views import about, contacts, delivery, home

urlpatterns = [
    path("home/", home, name="home"),
    path("contacts/", contacts, name="contacts"),
    path("about/", about, name="about"),
    path("delivery/", delivery, name="delivery"),
]
