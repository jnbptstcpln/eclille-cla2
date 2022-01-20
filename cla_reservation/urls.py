from django.urls import path, include
from cla_reservation.views import association

app_name = "cla_reservation"
urlpatterns = [
    path('', include(
        (
            [
                #path("", public.ListView.as_view(), name="list"),
                #path("<str:slug>", public.DetailView.as_view(), name="detail")
            ], 'manage'
        )
    )),
    path('', include(
        (
            [
                path("associations/<str:slug>/<int:pk>/barbecue", association.ReservationBarbecueView.as_view(), name="barbecue"),
                path("associations/<str:slug>/<int:pk>/foyer", association.ReservationFoyerView.as_view(), name="foyer"),
                path("associations/<str:slug>/<int:pk>/synthe", association.ReservationSyntheView.as_view(), name="synthe"),
            ], 'association'
        )
    ))
]
