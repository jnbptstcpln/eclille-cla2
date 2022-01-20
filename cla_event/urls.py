from django.urls import path, include
from cla_event.views import association

app_name = "cla_event"
urlpatterns = [
    path('', include(
        (
            [
                #path("", public.ListView.as_view(), name="list"),
                #path("<str:slug>", public.DetailView.as_view(), name="detail")
            ], 'public'
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
