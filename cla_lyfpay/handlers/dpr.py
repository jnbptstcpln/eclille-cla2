
from django.http import HttpResponse
from cla_lyfpay.models import Payment

class DancingPartyHandler:
    
    NAME = Payment.Origin.DANCING_PARTY_REGISTRATION.value
    
    @classmethod
    def validate(cls, payment: Payment) -> HttpResponse:
        return HttpResponse('OK')
    
    @classmethod
    def success(cls, payment: Payment)  -> HttpResponse:
        return HttpResponse('success')
    
    @classmethod
    def cancel(cls, payment: Payment)  -> HttpResponse:
        return HttpResponse('cancel')
    
    @classmethod
    def error(cls, payment: Payment)  -> HttpResponse:
        return HttpResponse('error')