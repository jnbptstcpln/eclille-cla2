from django.urls import path, include
from cla_reservation.views import association, manage

app_name = "cla_reservation"
urlpatterns = [
    path('', include(
        (
            [
                path("", manage.IndexView.as_view(), name="index"),
                path("foyer/", manage.FoyerListView.as_view(), name="foyer"),
                path("foyer/<int:pk>/", manage.FoyerDetailView.as_view(), name="foyer-detail"),
                path("foyer/<int:pk>/modifier/", manage.FoyerUpdateView.as_view(), name="foyer-update"),
                path("foyer/<int:pk>/valider/", manage.FoyerValidateView.as_view(), name="foyer-validate"),
                path("foyer/<int:pk>/rejeter/", manage.FoyerRejectView.as_view(), name="foyer-reject"),
                path("barbecue/", manage.BarbecueListView.as_view(), name="barbecue"),
                path("barbecue/<int:pk>/", manage.BarbecueDetailView.as_view(), name="barbecue-detail"),
                path("barbecue/<int:pk>/modifier/", manage.BarbecueUpdateView.as_view(), name="barbecue-update"),
                path("barbecue/<int:pk>/valider/", manage.BarbecueValidateView.as_view(), name="barbecue-validate"),
                path("barbecue/<int:pk>/rejeter/", manage.BarbecueRejectView.as_view(), name="barbecue-reject"),
                path("synthe/", manage.SyntheListView.as_view(), name="synthe"),
                path("synthe/<int:pk>/", manage.SyntheDetailView.as_view(), name="synthe-detail"),
                path("synthe/<int:pk>/modifier/", manage.SyntheUpdateView.as_view(), name="synthe-update"),
                path("synthe/<int:pk>/valider/", manage.SyntheValidateView.as_view(), name="synthe-validate"),
                path("synthe/<int:pk>/rejeter/", manage.SyntheRejectView.as_view(), name="synthe-reject"),
            ], 'manage'
        )
    )),
    path('', include(
        (
            [
                path("associations/<str:slug>/<int:pk>/barbecue", association.ReservationBarbecueView.as_view(), name="barbecue"),
                path("associations/<str:slug>/<int:pk>/barbecue/supprimer/", association.ReservationBarbecueDeleteView.as_view(), name="barbecue-delete"),
                path("associations/<str:slug>/<int:pk>/foyer", association.ReservationFoyerView.as_view(), name="foyer"),
                path("associations/<str:slug>/<int:pk>/foyer/supprimer/", association.ReservationFoyerDeleteView.as_view(), name="foyer-delete"),
                path("associations/<str:slug>/<int:pk>/synthe", association.ReservationSyntheView.as_view(), name="synthe"),
                path("associations/<str:slug>/<int:pk>/synthe/supprimer/", association.ReservationSyntheDeleteView.as_view(), name="synthe-delete"),
            ], 'association'
        )
    ))
]
