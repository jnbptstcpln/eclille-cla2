import io

from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import redirect, resolve_url, render
from django.template.loader import render_to_string
from django.views.generic import CreateView, FormView
from django_weasyprint import WeasyTemplateResponse
from weasyprint import HTML

from cla_association.models import Association
from cla_registration.forms import ImageRightForm, ImageRightSignForm
from cla_registration.models import ImageRightAgreement


class CreateAgreementView(CreateView):
    template_name = "cla_registration/imageright/form.html"
    form_class = ImageRightForm
    model = ImageRightAgreement

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'associations': {
                'cla': Association.objects.get_cla(),
                'bde': Association.objects.get_bde()
            }
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'school_domain': 'centrale.centralelille.fr'
        })
        return kwargs

    def get_success_url(self):
        return resolve_url("cla_registration:imageright_sign", self.object.pk)


class SignAgreementView(FormView):
    image_right_agreement: ImageRightAgreement = None
    template_name = "cla_registration/imageright/sign.html"
    form_class = ImageRightSignForm

    def dispatch(self, request, *args, **kwargs):
        try:
            self.image_right_agreement = ImageRightAgreement.objects.get(pk=kwargs.pop("pk", None))
        except ImageRightAgreement.DoesNotExist:
            return redirect("cla_registration:imageright_form")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        signature = form.cleaned_data['signature']
        # Generate the PDF
        pdf_factory = HTML(
            string=render_to_string(
                "cla_registration/imageright/pdf.html",
                {
                    'image_right_agreement': self.image_right_agreement,
                    'associations': {
                        'cla': Association.objects.get_cla(),
                        'bde': Association.objects.get_bde()
                    },
                    'signature': signature
                }
            ),
            base_url=self.request.build_absolute_uri()
        )
        self.image_right_agreement.file.save("generated_pdf.pdf", ContentFile(pdf_factory.write_pdf()), True)

        # Implement save logic
        return render(
            self.request,
            "cla_registration/imageright/signed.html",
            {
                'associations': {
                    'cla': Association.objects.get_cla(),
                    'bde': Association.objects.get_bde()
                }
            }
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'image_right_agreement': self.image_right_agreement,
            'associations': {
                'cla': Association.objects.get_cla(),
                'bde': Association.objects.get_bde()
            }
        })
        return context
