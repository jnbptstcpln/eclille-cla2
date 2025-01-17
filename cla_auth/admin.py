import copy

from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.contrib.admin import SimpleListFilter
from django.shortcuts import redirect
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.http import Http404, HttpRequest
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url
from django.utils.html import mark_safe, escape
from django.conf import settings
from django.utils import timezone

from cla_registration.views.admin import MembershipProofView
from cla_web.utils import current_school_year
from cla_auth.forms.admin_user_form import UserCreationForm, UserChangeForm
from cla_registration.models import Registration, ImageRightAgreement
from .models import UserInfos, UserMembership, Service, PasswordResetRequest

# Remove default User management interface
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(UserAdmin):
    class UserInfosInline(admin.StackedInline):
        model = UserInfos
        verbose_name = "Informations complémentaires"
        fields = (
            'account_type',
            'email_school',
            'birthdate',
            ('promo', 'cursus'),
            ('activated_on', 'valid_until'),
            'phone',
            'original_school',
            'image_right_agreement'
        )
        readonly_fields = 'activated_on', 'original_school', 'image_right_agreement'
        extra = 1
        min_num = 1
        can_delete = False

        def image_right_agreement(self, obj: UserInfos):
            image_right_agreement = obj.get_image_right_agreement()
            if image_right_agreement and image_right_agreement.file.name:
                return mark_safe(f"<a href='{image_right_agreement.file.url}' target='_blank'>Voir</a>")
            return "Aucun document correspondant"

        image_right_agreement.short_description = 'Formulaire de droit à l\'image'

    class MembershipInline(admin.StackedInline):
        model = UserMembership
        fields = (
            ('amount', 'paid_validated', 'proof'),
            ('paid_by', 'paiement_method', 'paid_on'),
            ('refunded', 'refunded_amount', 'refunded_on')
        )
        readonly_fields = ("proof",)
        extra = 0
        min_num = 0

        def proof(self, obj: UserMembership):
            return mark_safe(
                (
                    "<a href='{}' target='_blank'>Accéder</a>"
                ).format(resolve_url('admin:auth_user_membership', obj.user.pk))
            )
        proof.short_description = 'Attestation de cotisation'

    fieldsets = (
        (
            _('Personal info'),
            {
                'fields': ['account_status', 'first_name', 'last_name', 'email']
            }
        ),
        (
            "Information de connexion",
            {
                'fields': ('username', ('last_login', 'date_joined')),
                'classes': ('collapse',),
            }
        ),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
                'classes': ('collapse',),
            }
        ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (('first_name', 'last_name'), 'email'),
        }),
    )
    readonly_fields = 'account_status', 'username', 'last_login', 'date_joined', 'link_activation', 'link_reset'
    inlines = [
        UserInfosInline,
        MembershipInline,
    ]
    list_display = ('username', 'first_name', 'last_name', 'cursus', 'promo', 'is_activated', 'is_validated', 'paiement_validated')

    class ValidatedFilter(SimpleListFilter):
        title = 'statut du compte'
        parameter_name = 'validated'

        def lookups(self, request, model_admin):
            return [(1, "Compte validé"), (2, "Compte activé")]

        def queryset(self, request, queryset):
            raw_val = self.value()
            if raw_val is not None:
                val = int(raw_val)
                if val == 1:
                    return queryset.filter(infos__valid_until__gt=timezone.now())
                elif val == 2:
                    return queryset.filter(infos__activated_on__isnull=False)
            return queryset    

    class SchoolFilter(SimpleListFilter):
        title = 'école'
        parameter_name = 'school'

        def lookups(self, request, model_admin):
            return Registration.SchoolDomains.choices

        def queryset(self, request, queryset):
            if self.value() is not None:
                return queryset.filter(infos__email_school__endswith=f"@{self.value()}")
            else:
                return queryset
    
    class PromotionFilter(SimpleListFilter):
        title = 'promotion'
        parameter_name = 'promo'

        def lookups(self, request, model_admin):
            if request.GET.get(UserAdmin.SchoolFilter.parameter_name):
                y = current_school_year()
                return [(y + i, y + i) for i in range(6)]
            return []

        def queryset(self, request, queryset):
            if self.value() is not None:
                return queryset.filter(infos__promo=self.value())
            else:
                return queryset
    
    class PaiementFilter(SimpleListFilter):
        title = 'cotisation'
        parameter_name = 'paiement'

        def lookups(self, request, model_admin):
            return [(1, "Paiement non validé")]

        def queryset(self, request, queryset):
            raw_val = self.value()
            if raw_val is not None:
                val = int(raw_val)
                if val == 1:
                    return queryset.filter(membership__paid_validated=False)
            return queryset
    
    list_filter = (SchoolFilter, PromotionFilter, PaiementFilter, ValidatedFilter, 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    form = UserChangeForm
    add_form = UserCreationForm

    def email_school(self, obj: User):
        return obj.infos.email_school

    email_school.short_description = 'Email école'

    def cursus(self, obj: User):
        return obj.infos.cursus

    cursus.short_description = 'Cursus'

    def promo(self, obj: User):
        return obj.infos.promo

    promo.short_description = 'Promotion'

    def is_activated(self, obj: User):
        return obj.infos.activated_on is not None

    is_activated.short_description = 'Activé'
    is_activated.boolean = True

    def is_validated(self, obj: User):
        return obj.infos.valid_until is not None and obj.infos.valid_until > timezone.now()

    is_validated.short_description = 'Validé'
    is_validated.boolean = True

    def account_status(self, obj: User):
        if hasattr(obj, 'infos'):
            if not obj.infos.is_activated():
                return mark_safe("Ce compte n'a encore été activé")
            elif not obj.infos.is_valid():
                return mark_safe(
                    (
                        "Ce compte n'a encore été validé pour cette année scolaire "
                    )
                )
            else:
                return mark_safe(
                    (
                        "Ce compte est activé et validé pour cette année scolaire (jusqu'au {})"
                    ).format(obj.infos.valid_until.strftime("%d/%m/%Y"))
                )
        else:
            return "Ce compte n'est qu'un compte de gestion"

    account_status.short_description = 'Statut du compte'

    def link_reset(self, obj: User):
        return mark_safe(
            (
                "<label style='float:none;width:100%'>Transmettez le lien suivant à l'utilisateur pour qu'il puisse procéder à la réinitilisation de son mot de passe</label>"
                "<input style='margin-right: .5rem' class='vTextField' value='{reset_jwt}' id='id_reset_jwt'>"
                "<a class='button' onclick='document.getElementById(\"id_reset_jwt\").select();document.execCommand(\"copy\");return false;','>Copier</a>"
            ).format(reset_jwt=f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_auth:reset', obj.infos.reset_request.get_reset_jwt(exp=False))}")
        )

    link_reset.short_description = ""

    def link_activation(self, obj: User):
        return mark_safe(
            (
                "<label style='float:none;width:100%'>Transmettez le lien suivant à l'utilisateur pour qu'il puisse procéder à l'activation de son compte</label>"
                "<input style='margin-right: .5rem' class='vTextField' value='{activation_jwt}' id='id_activation_jwt'>"
                "<a class='button' onclick='document.getElementById(\"id_activation_jwt\").select();document.execCommand(\"copy\");return false;','>Copier</a>"
            ).format(activation_jwt=f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_auth:activate', obj.infos.activation_jwt)}")
        )

    link_activation.short_description = 'Activation du compte'
    
    def paiement_validated(self, obj: User):
        if hasattr(obj, 'membership'):
            return obj.membership.paid_validated
        return False

    paiement_validated.short_description = 'Cotisation'
    paiement_validated.boolean = True

    def get_fieldsets(self, request, obj: User = None):
        fieldsets = copy.deepcopy(super().get_fieldsets(request, obj))
        if obj is not None:
            # Il est nécessaire d'avoir la permission `manage_user_activation` pour accéder au lien d'activation du compte
            if request.user.has_perm("cla_auth.manage_user_activation") and not obj.infos.is_activated():
                fieldsets[0][1]['fields'] = ['link_activation'] + fieldsets[0][1]['fields']
            # Il est nécessaire d'avoir la permission `manage_user_password` pour accéder au champ de modification du mot de passe
            if request.user.has_perm("cla_auth.manage_user_password"):
                fieldsets[1][1]['fields'] = list(fieldsets[1][1]['fields'][:1]) + ['password'] + list(fieldsets[1][1]['fields'][1:])
                # Détection et affichage si une requête de réinitialisation est en cours
                reset_request = PasswordResetRequest.objects.get_current_reset_request(obj)
                if reset_request:
                    fieldsets[0][1]['fields'] = ['link_reset'] + fieldsets[0][1]['fields']
        return fieldsets

    def get_urls(self):
        return [
                   path(
                       '<id>/password-reset',
                       self.admin_site.admin_view(self.user_reset_password),
                       name='auth_user_password_reset',
                   ),
                   path(
                       '<pk>/preuve-cotisation',
                       self.admin_site.admin_view(MembershipProofView.as_view()),
                       name='auth_user_membership',
                   ),
               ] + super().get_urls()

    def save_model(self, request, obj: User, form, change):
        super().save_model(request, obj, form, change)

        if hasattr(obj, 'infos') and not change:
            messages.success(request, f"Un mail de bienvenue a été envoyé à {obj.infos.email_school} avec un lien d'activation")

    def user_reset_password(self, req, id, form_url=''):
        user = self.get_object(req, id)
        if not req.user.has_perm("cla_auth.manage_user_password"):
            raise PermissionDenied
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        PasswordResetRequest.objects.get_or_create_reset_request(user, count_attempt=False)
        self.log_change(req, user, "Password reset link created")
        messages.success(req, "Lien de réinitialisation de mot de passe créé, il est disponible en haut de cette page")
        return redirect(f"{self.admin_site.name}:{user._meta.app_label}_{user._meta.model_name}_change", user.pk)

    def has_view_permission(self, request: HttpRequest, obj: User = None):
        perm = super().has_view_permission(request, obj)
        if request.user.has_perm("cla_auth.autocomplete_user"):  # Allow user with `cla_auth:autocomplete_user` to access user list
            perm = True
        return perm


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Informations générales",
            {
                'fields': ('identifier', 'name', 'domain', 'endpoint'),
                'classes': ('wide',)
            }
        ),
        (
            "Gestion des connexions",
            {
                'fields': ('validation_required', 'authorization_required', 'auto_login', 'colleges'),
            }
        ),
        (
            "Dernières connexions",
            {
                'fields': ('last_tickets',),
                'classes': ('wide', 'collapse')
            }
        )
    )
    add_fieldsets = (
        (None, {
            'fields': ('identifier', 'name', 'domain', 'endpoint'),
            'classes': ('wide',),
        }),
    )
    readonly_fields = ('identifier', 'last_tickets',)

    def last_tickets(self, obj: Service):
        return mark_safe("<ul style='margin-left: 30px'>{}</ul>".format("".join(
            [
                f"<li>[{ticket.created_on.strftime('%d/%m/%Y %H:%M')}] {ticket.user.first_name} {ticket.user.last_name}</li>"
                for ticket in obj.tickets.all().order_by("-created_on")[:20]
            ]
        )))

    last_tickets.short_description = ''

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return self.readonly_fields
        return tuple()
