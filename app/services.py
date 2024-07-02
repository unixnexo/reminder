import os
from typing import Optional

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings

from .models import User


def send_sign_in_email(user: User) -> None:
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_link = f"{settings.EMAIL_VERIFICATION_URL}/{uid}/{token}/"

    subject = 'Verify your email address 📩'
    message = (
        '<div style="background-color:#1D232A;color:white;height:50vh;padding:20px;border-radius:20px;font-size:25px;text-align:center;">'
        '🌎 This is from riminder.pythonanywhere.com 🌎<br/>'
        'Please click '
        f'<a style="color:red;font-weight:bolder;" href="{verification_link}" target="_blank">HERE</a> '
        'to verify your email address<br/><br/>'
        'Ignore this email if you haven\'t requested it.'
        '</div>'
    )
    send_mail(subject, '', settings.EMAIL_HOST_USER, [user.email], html_message=message)


def decode_uid(uidb64: str) -> Optional[str]:
    """Decode the base64 encoded UID."""
    try:
        return urlsafe_base64_decode(uidb64).decode()
    except (TypeError, ValueError, OverflowError) as e:
        print(f'{e = }')
        return None


def get_user_by_uid(uid: str) -> Optional[User]:
    """Retrieve user object using UID."""
    try:
        return User.objects.get(pk=uid)
    except User.DoesNotExist as e:
        print(f'{e = }')
        return None
