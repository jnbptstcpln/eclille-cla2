from django.contrib import messages
from django.db.models import Q
from django.shortcuts import resolve_url, get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView


class AbstractBlockedSlotView:
    cla_reservation_active_section = "blockedslot"
    infrastructure_name = None
    infrastructure_id = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'infrastructure_name': self.infrastructure_name
        })
        return context


class AbstractBlockedSlotListView(AbstractBlockedSlotView, ListView):
    template_name = "cla_reservation/manage/_blockedslot/list.html"
    paginate_by = 20
    model = None

    def get_queryset(self):
        return self.model.objects.filter(Q(ends_on__gte=timezone.now()) | Q(recurring=True, end_recurring__gte=timezone.now()) | Q(recurring=True, end_recurring__isnull=True))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'create_href': resolve_url(f"cla_reservation:manage:{self.infrastructure_id}-blockedslot-create"),
            'detail_url_scheme': f"cla_reservation:manage:{self.infrastructure_id}-blockedslot-update"
        })
        return context


class AbstractBlockedSlotCreateView(AbstractBlockedSlotView, CreateView):
    template_name = "cla_reservation/manage/_blockedslot/create.html"
    model = None

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Le créneaux a bien été créé")
        return response

    def get_success_url(self):
        return resolve_url(f"cla_reservation:manage:{self.infrastructure_id}-blockedslot-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'back_href': resolve_url(f"cla_reservation:manage:{self.infrastructure_id}-blockedslot-list")
        })
        return context


class AbstractBlockedSlotUpdateView(AbstractBlockedSlotView, UpdateView):
    template_name = "cla_reservation/manage/_blockedslot/update.html"
    model = None

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Les changements ont bien été enregistrés")
        return response

    def get_success_url(self):
        return resolve_url(f"cla_reservation:manage:{self.infrastructure_id}-blockedslot-update", self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'delete_href': resolve_url(f"cla_reservation:manage:{self.infrastructure_id}-blockedslot-delete", self.object.pk),
            'back_href': resolve_url(f"cla_reservation:manage:{self.infrastructure_id}-blockedslot-list")
        })
        return context


class AbstractBlockedSlotDeleteView(AbstractBlockedSlotView, View):
    model = None
    object = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.object = get_object_or_404(self.model, pk=kwargs.pop('pk'))

    def get(self, request, *args, **kwargs):
        return resolve_url(f"cla_reservation:manage:{self.infrastructure_id}-blockedslot-update", self.object.pk)

    def post(self, request, *args, **kwargs):
        self.object.delete()
        messages.info(self.request, "Le créneau a bien été supprimé")

        return redirect(f"cla_reservation:manage:{self.infrastructure_id}-blockedslot-list")
