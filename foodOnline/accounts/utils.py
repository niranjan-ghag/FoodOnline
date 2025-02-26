from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from django.conf import settings

def detectUser(user):
    if user.role == 1:
        redirect_url = 'vendordashboard'
    elif user.role == 0:
        redirect_url = 'custdashboard'
    elif user.role ==None and user.is_superadmin:
        redirect_url = '/admin'
    
    return redirect_url

def send_verification_email(request,user, email_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    mail_subject = email_subject
    message = render_to_string(email_template, {
        'user':user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
    })
    to_email = user.email
    mail = EmailMessage(mail_subject, message,from_email, to=[to_email])
    mail.send()

# def send_reset_password_email(request,user):
#     from_email = settings.DEFAULT_FROM_EMAIL
#     current_site = get_current_site(request)
#     mail_subject = 'Reset Password'
#     message = render_to_string('accounts/emails/reset_password_email.html', {
#         'user':user,
#         'domain': current_site,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': default_token_generator.make_token(user)
#     })
#     to_email = user.email
#     mail = EmailMessage(mail_subject, message,from_email, to=[to_email])
#     mail.send()
