from django.urls import path, include

from cla_reservation.mixins import PlanningSchoolAdminMixin
from cla_reservation.views import association, manage, public, school_admin

app_name = "cla_reservation"
urlpatterns = [
    path('', public.IndexView.as_view(), name="index"),
    path('', include(
        (
            [
                path("planning/barbecue/", public.PlanningBarbecueView.as_view(), name="barbecue-planning"),
                path("planning/bibli/", public.PlanningBibliView.as_view(), name="bibli-planning"),
                path("planning/foyer/", public.PlanningFoyerView.as_view(), name="foyer-planning"),
                path("planning/synthe/", public.PlanningSyntheView.as_view(), name="synthe-planning"),
                path("reserver/barbecue/", public.ReservationBarbecueView.as_view(), name="barbecue-reservation"),
                path("reserver/bibli/", public.ReservationBibliView.as_view(), name="bibli-reservation"),
                path("reserver/foyer/", public.ReservationFoyerView.as_view(), name="foyer-reservation"),
                path("reserver/synthe/", public.ReservationSyntheView.as_view(), name="synthe-reservation"),
            ], 'public'
        )
    )),
    path('', include(
        (
            [
                path("barbecue/", manage.barbecue.BarbecueListView.as_view(), name="barbecue"),
                path("barbecue/planning/", manage.barbecue.BarbecuePlanningView.as_view(), name="barbecue-planning"),
                path("barbecue/planning/export/ical", manage.barbecue.BarbecueIcsFileView.as_view(), name="barbecue-export"),
                path("barbecue/creneaux-bloques/", manage.barbecue.BarbecueBlockedSlotListView.as_view(), name="barbecue-blockedslot-list"),
                path("barbecue/creneaux-bloques/nouveau", manage.barbecue.BarbecueBlockedSlotCreateView.as_view(), name="barbecue-blockedslot-create"),
                path("barbecue/creneaux-bloques/<int:pk>", manage.barbecue.BarbecueBlockedSlotUpdateView.as_view(), name="barbecue-blockedslot-update"),
                path("barbecue/creneaux-bloques/<int:pk>/supprimer", manage.barbecue.BarbecueBlockedSlotDeleteView.as_view(), name="barbecue-blockedslot-delete"),
                path("barbecue/<int:pk>/", manage.barbecue.BarbecueDetailView.as_view(), name="barbecue-detail"),
                path("barbecue/<int:pk>/modifier/", manage.barbecue.BarbecueUpdateView.as_view(), name="barbecue-update"),
                path("barbecue/<int:pk>/valider/", manage.barbecue.BarbecueValidateView.as_view(), name="barbecue-validate"),
                path("barbecue/<int:pk>/rejeter/", manage.barbecue.BarbecueRejectView.as_view(), name="barbecue-reject"),
                path("bibli/", manage.bibli.BibliListView.as_view(), name="bibli"),
                path("bibli/planning/", manage.bibli.BibliPlanningView.as_view(), name="bibli-planning"),
                path("bibli/planning/export/ical", manage.bibli.BibliIcsFileView.as_view(), name="bibli-export"),
                path("bibli/creneaux-bloques/", manage.bibli.BibliBlockedSlotListView.as_view(), name="bibli-blockedslot-list"),
                path("bibli/creneaux-bloques/nouveau", manage.bibli.BibliBlockedSlotCreateView.as_view(), name="bibli-blockedslot-create"),
                path("bibli/creneaux-bloques/<int:pk>", manage.bibli.BibliBlockedSlotUpdateView.as_view(), name="bibli-blockedslot-update"),
                path("bibli/creneaux-bloques/<int:pk>/supprimer", manage.bibli.BibliBlockedSlotDeleteView.as_view(), name="bibli-blockedslot-delete"),
                path("bibli/<int:pk>/", manage.bibli.BibliDetailView.as_view(), name="bibli-detail"),
                path("bibli/<int:pk>/modifier/", manage.bibli.BibliUpdateView.as_view(), name="bibli-update"),
                path("bibli/<int:pk>/valider/", manage.bibli.BibliValidateView.as_view(), name="bibli-validate"),
                path("bibli/<int:pk>/rejeter/", manage.bibli.BibliRejectView.as_view(), name="bibli-reject"),
                path("foyer/", manage.foyer.FoyerListView.as_view(), name="foyer"),
                path("foyer/planning/", manage.foyer.FoyerPlanningView.as_view(), name="foyer-planning"),
                path("foyer/planning/export/ical", manage.foyer.FoyerIcsFileView.as_view(), name="foyer-export"),
                path("foyer/creneaux-bloques/", manage.foyer.FoyerBlockedSlotListView.as_view(), name="foyer-blockedslot-list"),
                path("foyer/creneaux-bloques/nouveau", manage.foyer.FoyerBlockedSlotCreateView.as_view(), name="foyer-blockedslot-create"),
                path("foyer/creneaux-bloques/<int:pk>", manage.foyer.FoyerBlockedSlotUpdateView.as_view(), name="foyer-blockedslot-update"),
                path("foyer/creneaux-bloques/<int:pk>/supprimer", manage.foyer.FoyerBlockedSlotDeleteView.as_view(), name="foyer-blockedslot-delete"),
                path("foyer/<int:pk>/", manage.foyer.FoyerDetailView.as_view(), name="foyer-detail"),
                path("foyer/<int:pk>/modifier/", manage.foyer.FoyerUpdateView.as_view(), name="foyer-update"),
                path("foyer/<int:pk>/valider/", manage.foyer.FoyerValidateView.as_view(), name="foyer-validate"),
                path("foyer/<int:pk>/rejeter/", manage.foyer.FoyerRejectView.as_view(), name="foyer-reject"),
                path("synthe/", manage.synthe.SyntheListView.as_view(), name="synthe"),
                path("synthe/planning/", manage.synthe.SynthePlanningView.as_view(), name="synthe-planning"),
                path("synthe/planning/export/ical", manage.synthe.SyntheIcsFileView.as_view(), name="synthe-export"),
                path("synthe/creneaux-bloques/", manage.synthe.SyntheBlockedSlotListView.as_view(), name="synthe-blockedslot-list"),
                path("synthe/creneaux-bloques/nouveau", manage.synthe.SyntheBlockedSlotCreateView.as_view(), name="synthe-blockedslot-create"),
                path("synthe/creneaux-bloques/<int:pk>", manage.synthe.SyntheBlockedSlotUpdateView.as_view(), name="synthe-blockedslot-update"),
                path("synthe/creneaux-bloques/<int:pk>/supprimer", manage.synthe.SyntheBlockedSlotDeleteView.as_view(), name="synthe-blockedslot-delete"),
                path("synthe/<int:pk>/", manage.synthe.SyntheDetailView.as_view(), name="synthe-detail"),
                path("synthe/<int:pk>/modifier/", manage.synthe.SyntheUpdateView.as_view(), name="synthe-update"),
                path("synthe/<int:pk>/valider/", manage.synthe.SyntheValidateView.as_view(), name="synthe-validate"),
                path("synthe/<int:pk>/rejeter/", manage.synthe.SyntheRejectView.as_view(), name="synthe-reject"),
            ], 'manage'
        )
    )),
    path('', include(
        (
            [
                path("associations/<str:slug>/<int:pk>/barbecue", association.ReservationBarbecueView.as_view(), name="barbecue"),
                path("associations/<str:slug>/<int:pk>/barbecue/supprimer/", association.ReservationBarbecueDeleteView.as_view(), name="barbecue-delete"),
                path("associations/<str:slug>/<int:pk>/bibli", association.ReservationBibliView.as_view(), name="bibli"),
                path("associations/<str:slug>/<int:pk>/bibli/supprimer/", association.ReservationBibliDeleteView.as_view(), name="bibli-delete"),
                path("associations/<str:slug>/<int:pk>/foyer", association.ReservationFoyerView.as_view(), name="foyer"),
                path("associations/<str:slug>/<int:pk>/foyer/supprimer/", association.ReservationFoyerDeleteView.as_view(), name="foyer-delete"),
                path("associations/<str:slug>/<int:pk>/synthe", association.ReservationSyntheView.as_view(), name="synthe"),
                path("associations/<str:slug>/<int:pk>/synthe/supprimer/", association.ReservationSyntheDeleteView.as_view(), name="synthe-delete"),
            ], 'association'
        )
    )),
    path('', include(
        (
            [
                path(f"barbecue/ec/{PlanningSchoolAdminMixin.TOKEN_BARBECUE}", school_admin.BarbecueView.as_view(), name="barbecue"),
                path(f"bibli/ec/{PlanningSchoolAdminMixin.TOKEN_BIBLI}", school_admin.BibliView.as_view(), name="bibli"),
                path(f"foyer/ec/{PlanningSchoolAdminMixin.TOKEN_FOYER}", school_admin.FoyerView.as_view(), name="foyer"),
                path(f"synthe/ec/{PlanningSchoolAdminMixin.TOKEN_SYNTHE}", school_admin.SyntheView.as_view(), name="synthe")
            ], 'school_admin'
        )
    )),
]
