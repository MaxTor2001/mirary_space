from django.urls import path

from .views import about, contacts, delivery, home, offer_document, privacy_document

urlpatterns = [
    path("home/", home, name="home"),
    path("contacts/", contacts, name="contacts"),
    path("about/", about, name="about"),
    path("delivery/", delivery, name="delivery"),
    path("offer/", offer_document, name="offer"),
    path("privacy/", privacy_document, name="privacy"),
]
