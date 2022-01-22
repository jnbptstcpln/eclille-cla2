from django.urls import path, include
from cla_event.views import association, public, manage

app_name = "cla_event"
urlpatterns = [
    path('', include(
        (
            [
                path("", public.IndexView.as_view(), name="index")
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
            ], 'association'
        )
    ))
]
