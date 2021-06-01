from django.urls import path

from cla_ticketing.views import event

app_name = "cla_ticketing"
urlpatterns = [
    path("<str:event_slug>", event.ticketing, name="event_ticketing")
]
