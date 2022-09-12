
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from dataclasses import dataclass

@dataclass
class PaymentRequest:

    merchant: str
    wallet: str
    origin: str
    reference: str
    lyfpay_amount: int
    
    @classmethod
    def get_jwt(cls, merchant, wallet, origin, reference, lyfpay_amount):
        return jwt.encode(
            payload={
                'merchant': merchant,
                'wallet': wallet,
                'origin': origin,
                'reference': reference,
                'lyfpay_amount': lyfpay_amount,
                'exp': datetime.utcnow() + timedelta(seconds=10)  # Token is valid for 10 seconds
            },
            key=settings.SECRET_KEY,
            algorithm="HS256"
        )
    
    @classmethod
    def parse_jwt(cls, token):
        try:
            payload = jwt.decode(
                jwt=token,
                key=settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            payload.pop('exp', None)
            return cls(**payload)            
        except:
            return None