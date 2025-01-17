from django.urls import path, include

from cla_event.mixins import PlanningSchoolAdminMixin
from cla_event.views import association, public, manage, school_admin

app_name = "cla_event"
urlpatterns = [
    path('', include(
        (
            [
                path("", public.IndexView.as_view(), name="index"),
                path("export/ical/", public.IcsFileView.as_view(), name="export"),
            ], 'public'
        )
    )),
    path('', include(
        (
            [
                path("modifier/", manage.IndexView.as_view(), name="index"),
                path("modifier/<int:pk>/", manage.EventDetailView.as_view(), name="event-detail"),
                path("modifier/<int:pk>/modifier", manage.EventUpdateView.as_view(), name="event-update"),
                path("modifier/<int:pk>/valider", manage.EventValidateView.as_view(), name="event-validate"),
                path("modifier/<int:pk>/rejeter", manage.EventRejectView.as_view(), name="event-reject"),
                path("modifier/<int:pk>/annuler", manage.EventCancelView.as_view(), name="event-cancel"),
            ], 'manage'
        )
    )),
    path('', include(
        (
            [
                path("associations/<str:slug>/", association.EventListView.as_view(), name="list"),
                path("associations/<str:slug>/nouveau/", association.EventCreateView.as_view(), name="create"),
                path("associations/<str:slug>/<int:pk>/", association.EventUpdateView.as_view(), name="update"),
                path("associations/<str:slug>/<int:pk>/envoyer/", association.EventSendView.as_view(), name="send"),
                path("associations/<str:slug>/<int:pk>/annuler/", association.EventCancelView.as_view(), name="cancel"),
            ], 'association'
        )
    )),
    path('', include(
        (
            [
                path(f"ec/{PlanningSchoolAdminMixin.TOKEN}", school_admin.IndexView.as_view(), name="index"),
                path(f"ec/{PlanningSchoolAdminMixin.TOKEN}/ics", school_admin.IndexIcsView.as_view(), name="index-ics")
            ], 'school_admin'
        )
    )),
]
