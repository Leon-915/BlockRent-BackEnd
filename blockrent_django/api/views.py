from django.shortcuts import render
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import login
from api.models import User
from api.tokens import account_activation_token


# Create your views here.
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_encode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for your email confirmation.')
    else:
        return HttpResponse('Activation link is invalid!')
