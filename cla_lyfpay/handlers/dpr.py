
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from cla_lyfpay.models import Payment
from cla_ticketing.models import DancingPartyRegistration
from django.shortcuts import redirect

class DancingPartyHandler:
    
    NAME = Payment.Origin.DANCING_PARTY_REGISTRATION.value
    
    @classmethod
    def validate(cls, req: HttpRequest, payment: Payment) -> HttpResponse:
        dpr: DancingPartyRegistration = DancingPartyRegistration.objects.filter(pk=payment.reference).first()
        assert dpr, f'No dancing party registration found for pk=`{payment.reference}`'
        
        if payment.is_validated:
            dpr.paid = True
            dpr.lyfpay_payment = payment
            dpr.save()
        
        return HttpResponse('OK')
    
    @classmethod
    def success(cls, req: HttpRequest, payment: Payment)  -> HttpResponse:
        dpr: DancingPartyRegistration = DancingPartyRegistration.objects.filter(pk=payment.reference).first()
        assert dpr, f'No dancing party registration found for pk=`{payment.reference}`'
        
        messages.success(req, f"Votre paiement a bien été reçu et validé")
        
        return redirect(
            f'cla_ticketing:party_detail_{"contributor" if dpr.is_contributor else "noncontributor"}',
            dpr.dancing_party.slug
        )
    
    @classmethod
    def cancel(cls, req: HttpRequest, payment: Payment)  -> HttpResponse:
        dpr: DancingPartyRegistration = DancingPartyRegistration.objects.filter(pk=payment.reference).first()
        assert dpr, f'No dancing party registration found for pk=`{payment.reference}`'
        
        messages.warning(req, f"Le paiement a été annulé")
        
        return redirect(
            f'cla_ticketing:party_detail_{"contributor" if dpr.is_contributor else "noncontributor"}',
            dpr.dancing_party.slug
        )
    
    @classmethod
    def error(cls, req: HttpRequest, payment: Payment)  -> HttpResponse:
        dpr: DancingPartyRegistration = DancingPartyRegistration.objects.filter(pk=payment.reference).first()
        assert dpr, f'No dancing party registration found for pk=`{payment.reference}`'
        
        messages.error(req, f"Une erreur s'est produite lors du paiement, veuillez contacter l'organisateur avec la référence suivante : `{payment.lyfpay_shop_reference}`")
                    
        return redirect(
            f'cla_ticketing:party_detail_{"contributor" if dpr.is_contributor else "noncontributor"}',
            dpr.dancing_party.slug
        )
