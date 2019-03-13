from django.core.mail import send_mail, EmailMessage
from blockrent_django.settings import EMAIL_HOST_USER
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from api.tokens import account_activation_token


def send_email_notification(email_list):
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = EMAIL_HOST_USER
    recipient_list = email_list
    send_mail(subject, message, email_from, recipient_list)


def send_application_confirm_email(tenant, owner, application):
    current_site = 'localhost:8080'
    subject = 'Application Confirmation'
    message_tenant = render_to_string('acc_active_application_email.html', {
        'user': tenant,
        'tenant': tenant,
        'owner': owner,
        'domain': current_site,
        'application': application
    })
    message_owner = render_to_string('acc_active_application_email.html', {
        'user': owner,
        'tenant': tenant,
        'owner': owner,
        'domain': current_site,
        'application': application
    })

    try:
        send_mail(subject, message_tenant, EMAIL_HOST_USER, [tenant.email, ])
    except:
        pass

    try:
        send_mail(subject, message_owner, EMAIL_HOST_USER, [owner.email, ])
    except:
        pass


def send_account_creation_email(user, password):
    current_site = 'localhost:8080'
    subject = 'Thank you for registering to our site'
    message = render_to_string('acc_active_email.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': account_activation_token.make_token(user),
        'password': password
    })

    email = EmailMessage(subject, message, to=[user.email, ], from_email=EMAIL_HOST_USER)
    try:
        email.send()
    except:
        pass
