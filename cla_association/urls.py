from django.urls import path, include
from cla_association.views import public, manage

app_name = "cla_association"
urlpatterns = [
    path('', include(
        (
            [
                path("", public.ListView.as_view(), name="list"),
                path("<str:slug>", public.DetailView.as_view(), name="detail")
            ], 'public'
        )
    )),
    path('', include(
        (
            [
                path("<str:slug>/gestion", manage.IndexView.as_view(), name="index"),
                path("<str:slug>/gestion/modifier", manage.ChangeView.as_view(), name="change"),
                path("<str:slug>/gestion/modifier/logo", manage.ChangeLogoView.as_view(), name="change_logo"),
                path("<str:slug>/gestion/responsables", manage.ManagersView.as_view(), name="managers"),
                path("<str:slug>/gestion/passations", manage.HandoverView.as_view(), name="handover"),
            ], 'manage'
        )
    ))
]
