import json
import time
import bugsnag
import shortuuid

from django.http import *
from django.conf import settings
from django.shortcuts import resolve_url
from django.utils import timezone
from django.contrib.auth.decorators import login_required


from cla_lyfpay.models import Wallet, Payment
from cla_lyfpay.jwt import PaymentRequest
from cla_lyfpay.api import LyfpayAPI
from cla_lyfpay.handlers import get_handler

from urllib.parse import urlencode
from base64 import b64encode

def debug(req: HttpRequest):
    token = PaymentRequest.get_jwt(
        wallet='test',
        origin=Payment.Origin.DANCING_PARTY_REGISTRATION,
        reference=12345,
        lyfpay_amount=1100
    )
    
    url = resolve_url('cla_lyfpay:payment', token=token)
    #return HttpResponse(url)
    return HttpResponseRedirect(url)

@login_required
def payment(req: HttpRequest, token):

    payment_request = PaymentRequest.parse_jwt(token)

    if not payment_request:
        raise HttpResponseBadRequest()

    # Generate a unique identifier for this payment
    lyfpay_shop_reference = shortuuid.uuid()

    # Callback with be used at the end of the payment process to redirect user to CLA website
    lyfpay_additional_data = json.dumps({
        'callback': f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_lyfpay:validate')}",
        'callbackEmail': 'cla@centralelille.fr'
    })

    # Build the parameter required by Lyfpay API
    #   --> https://merchant.lyf.eu/Assets/files/Lyf_Web_Plugin_into_an_ecommerce_platform.pdf
    lyfpay_params = {
        "additionalDataEncoded": b64encode(lyfpay_additional_data.encode()).decode(),
        "amount": str(payment_request.lyfpay_amount),
        "currency": "EUR",
        "deliveryFeesAmount": "0",
        "enforcedIdentification": "false",
        "lang": "fr",
        "mode": "IMMEDIATE",
        "onCancel": f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_lyfpay:cancel', lyfpay_shop_reference)}",
        "onError": f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_lyfpay:error', lyfpay_shop_reference)}",
        "onSuccess": f"https://{settings.ALLOWED_HOSTS[0]}{resolve_url('cla_lyfpay:success', lyfpay_shop_reference)}",
        "posUuid": settings.LYFPAY_POS,
        "shopOrderReference": f'{payment_request.origin}{payment_request.reference}',
        "shopReference": lyfpay_shop_reference,
        "timestamp": str(int(time.time())),
        "version": "v2.0"
    }
    
    # Get or create the attached wallet
    wallet, created = Wallet.objects.get_or_create(name=payment_request.wallet)

    # Set the request's seal
    lyfpay_params['mac'] = LyfpayAPI.get_payment_seal(
        lang=lyfpay_params['lang'],
        version=lyfpay_params['version'],
        timestamp=lyfpay_params['timestamp'],
        posUuid=lyfpay_params['posUuid'],
        shopReference=lyfpay_params['shopReference'],
        shopOrderReference=lyfpay_params['shopOrderReference'],
        deliveryFeesAmount=lyfpay_params['deliveryFeesAmount'],
        amount=lyfpay_params['amount'],
        currency=lyfpay_params['currency'],
        mode=lyfpay_params['mode'],
        onSuccess=lyfpay_params['onSuccess'],
        onCancel=lyfpay_params['onCancel'],
        onError=lyfpay_params['onError'],
        additionalData=lyfpay_additional_data,
        enforcedIdentification=lyfpay_params['enforcedIdentification']
    )

    # Save this payment attempt
    Payment.objects.create(
        wallet=wallet,
        origin=payment_request.origin,
        reference=payment_request.reference,
        lyfpay_amount=payment_request.lyfpay_amount,
        lyfpay_shop_reference=lyfpay_params['shopReference'],
        lyfpay_shop_order_reference=lyfpay_params['shopOrderReference'],
        created_by=req.user
    )

    # Redirect to Lyfpay website
    #return HttpResponseRedirect(f'https://sandbox-webpos.lyf.eu/fr/plugin/Payment.aspx?{urlencode(lyfpay_params)}')
    return HttpResponseRedirect(f'https://webpos.lyf.eu/fr/plugin/Payment.aspx?{urlencode(lyfpay_params)}')


def validate(req: HttpRequest):
    data = {
        'posUuid': req.POST["posUuid"],
        'shopReference': req.POST["shopReference"],
        'shopOrderReference': req.POST["shopOrderReference"],
        'amount': req.POST["amount"],
        'discount': req.POST["discount"],
        'currency': req.POST["currency"],
        'status': req.POST["status"],
        'creationDate': req.POST["creationDate"],
        'transactionUuid': req.POST["transactionUuid"],
        'additionalData': req.POST["additionalData"],
        'mac': req.POST["mac"]
    }

    try:
        seal = LyfpayAPI.get_handle_seal(
            posUuid=data['posUuid'],
            shopReference=data['shopReference'],
            shopOrderReference=data['shopOrderReference'],
            amount=data['amount'],
            discount=data['discount'],
            currency=data['currency'],
            status=data['status'],
            creationDate=data['creationDate'],
            transactionUuid=data['transactionUuid'],
            additionalData=data['additionalData']
        )
        assert data['mac'].upper() == seal, f"Seals don't match (`{seal}`)"
        
        payment: Payment = Payment.objects.filter(lyfpay_shop_reference=data['shopReference']).first()
        assert payment, f'No payment found'
        
        payment.lyfpay_updated_at = timezone.now()
        payment.lyfpay_id = data['transactionUuid']
        payment.lyfpay_status = data['status']
        payment.save()
        
        if payment.validated:
            handler = get_handler(payment.origin, 'validate')
            if handler:
                return handler(payment)
            else:
                bugsnag.notify(f'No payment handler found for origin `{payment.origin}` and event `validate`', metadata={'payment': payment.__dict__()})
        
    except Exception as e:
        bugsnag.notify(e, metadata={'data': data})
        raise e


def success(req: HttpRequest, token):    
    payment: Payment = Payment.objects.filter(lyfpay_shop_reference=token).first()    
    if payment:
        if payment.lyfpay_status != Payment.LyfpayStatus.VALIDATED:  # Check that the event have been validated
            raise HttpResponseForbidden()
        
        handler = get_handler(payment.origin, 'success')
        if handler:
            return handler(payment)
        else:
            bugsnag.notify(f'No payment handler found for origin `{payment.origin}` and event `success`', metadata={'payment': payment.__dict__()})
    raise Http404()


def cancel(req: HttpRequest, token):    
    payment: Payment = Payment.objects.filter(lyfpay_shop_reference=token).first()    
    if payment:
        if payment.lyfpay_status == Payment.LyfpayStatus.WAITING:
            payment.lyfpay_updated_at = timezone.now()
            payment.lyfpay_status = Payment.LyfpayStatus.REFUSED
            payment.save()
        
        handler = get_handler(payment.origin, 'cancel')
        if handler:
            return handler(payment)
        else:
            bugsnag.notify(f'No payment handler found for origin `{payment.origin}` and event `cancel`', metadata={'payment': payment.__dict__()})


def error(req: HttpRequest, token):    
    payment: Payment = Payment.objects.filter(lyfpay_shop_reference=token).first()    
    if payment:
        if payment.lyfpay_status == Payment.LyfpayStatus.WAITING:
            payment.lyfpay_updated_at = timezone.now()
            payment.lyfpay_status = Payment.LyfpayStatus.FAILED
            payment.save()
        
        handler = get_handler(payment.origin, 'error')
        if handler:
            return handler(payment)
        else:
            bugsnag.notify(f'No payment handler found for origin `{payment.origin}` and event `error`', metadata={'payment': payment.__dict__()})
    raise Http404()

