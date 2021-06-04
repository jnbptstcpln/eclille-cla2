import jwt
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone


class StayLoggedInMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not request.user.is_authenticated:
            user = self._get_user_from_jwt(request.COOKIES.get('stay_logged_in'))
            if user:
                auth.login(request, user)

        response = self.get_response(request)

        return response

    @classmethod
    def _get_user_from_jwt(cls, stay_logged_in_jwt=None) -> User:
        if stay_logged_in_jwt is None:
            return None

        # Retrieve jwt payload to fetch user
        try:
            jwt_payload = jwt.decode(stay_logged_in_jwt, algorithms=["HS256"], options={"verify_signature": False})
        except:
            return None

        try:
            user = User.objects.get(pk=jwt_payload.get('pk'))
        except User.DoesNotExist:
            return None

        try:
            payload = jwt.decode(
                jwt=stay_logged_in_jwt,
                key=f"{settings.SECRET_KEY}-{user.username}-{user.password}",
                algorithms=["HS256"]
            )
            return user
        except:
            return None

    @classmethod
    def get_jwt(self, user):
        return jwt.encode(
            payload={'pk': user.pk, 'exp': timezone.datetime.utcnow() + timezone.timedelta(days=30)},  # Stay logged in for 30 days
            key=f"{settings.SECRET_KEY}-{user.username}-{user.password}",
            algorithm="HS256"
        )
