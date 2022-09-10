import hmac
import hashlib

from django.conf import settings


class LyfpayAPI:

    @staticmethod
    def get_seal(*args):
        return hmac.new(
            settings.LYFPAY_KEY.encode('ascii'),
            '*'.join(args).encode('ascii'),
            hashlib.sha1
        ).hexdigest().upper()

    @classmethod
    def get_payment_seal(cls,
                         lang,
                         version,
                         timestamp,
                         posUuid,
                         shopReference,
                         shopOrderReference,
                         deliveryFeesAmount,
                         amount,
                         currency,
                         mode,
                         onSuccess,
                         onCancel,
                         onError,
                         additionalData,
                         enforcedIdentification):
        """
        Construct Lyfpay seal using a sha1 powered HMAC
        --> https://merchant.lyf.eu/Assets/files/Lyf_Web_Plugin_into_an_ecommerce_platform.pdf
        """
        return cls.get_seal(
            lang,
            version,
            timestamp,
            posUuid,
            shopReference,
            shopOrderReference,
            deliveryFeesAmount,
            amount,
            currency,
            mode,
            onSuccess,
            onCancel,
            onError,
            additionalData,
            enforcedIdentification
        )

    @classmethod
    def get_handle_seal(cls,
                        posUuid,
                        shopReference,
                        shopOrderReference,
                        amount,
                        discount,
                        currency,
                        status,
                        creationDate,
                        transactionUuid,
                        additionalData):
        """
        Construct Lyfpay seal using a sha1 powered HMAC
        --> https://merchant.lyf.eu/Assets/files/Lyf_Web_Plugin_into_an_ecommerce_platform.pdf
        """
        return cls.get_seal(
            posUuid,
            shopReference,
            shopOrderReference,
            amount,
            discount,
            currency,
            status,
            creationDate,
            transactionUuid,
            additionalData
        )
