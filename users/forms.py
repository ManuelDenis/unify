from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from unify import settings
from dj_rest_auth.app_settings import api_settings

if 'allauth' in settings.INSTALLED_APPS:
    from allauth.account import app_settings as allauth_account_settings
    from allauth.account.adapter import get_adapter
    from allauth.account.forms import ResetPasswordForm as DefaultPasswordResetForm
    from allauth.account.forms import default_token_generator
    from allauth.account.utils import (
        filter_users_by_email,
        user_pk_to_url_str,
        user_username,
    )
    from allauth.utils import build_absolute_uri


class CustomPasswordResetForm(DefaultPasswordResetForm):

    def default_url_generator(self, request, user, temp_key):
        """
        Generate the custom password reset URL, replacing the domain if needed.
        """
        # Construct the URL path for the password reset confirmation
        path = reverse(
            'password_reset_confirm',  # The route name for password reset confirmation
            args=[user_pk_to_url_str(user), temp_key],
        )

        # Customize the domain (use localhost:3000 in this example)
        custom_domain = "http://localhost:3000"
        url = build_absolute_uri(request, path).replace("http://127.0.0.1:8000", custom_domain)

        return url

    def clean_email(self):
        """
        Invalid email should not raise an error, as this would leak user existence.
        """
        email = self.cleaned_data["email"]
        email = get_adapter().clean_email(email)
        self.users = filter_users_by_email(email, is_active=True)
        return self.cleaned_data["email"]

    def save(self, request, **kwargs):
        """
        Override the save method to send a password reset email with a custom URL generator.
        """
        current_site = get_current_site(request)
        email = self.cleaned_data['email']
        token_generator = kwargs.get('token_generator', default_token_generator)

        for user in self.users:
            temp_key = token_generator.make_token(user)

            # Use the custom URL generator to create the reset URL
            url_generator = kwargs.get('url_generator', self.default_url_generator)
            url = url_generator(request, user, temp_key)
            uid = user_pk_to_url_str(user)

            context = {
                'current_site': current_site,
                'user': user,
                'password_reset_url': url,
                'request': request,
                'token': temp_key,
                'uid': uid,
            }

            if (
                allauth_account_settings.AUTHENTICATION_METHOD
                != allauth_account_settings.AuthenticationMethod.EMAIL
            ):
                context['username'] = user_username(user)

            # Send the password reset email
            get_adapter(request).send_mail(
                'account/email/password_reset_key', email, context
            )
        return self.cleaned_data['email']
