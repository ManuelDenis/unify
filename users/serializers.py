from dj_rest_auth.registration.serializers import RegisterSerializer
from users.forms import CustomPasswordResetForm
from users.models import CustomUser
from rest_framework import serializers
from django.conf import settings


class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Token-ul este necesar.")
        return value


class CustomRegisterSerializer(RegisterSerializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Această adresă de email este deja înregistrată. "
                "Dacă ai creat contul cu Google, te rugăm să te autentifici prin Google "
                "sau poți utiliza opțiunea de resetare a parolei."
            )
        return email


class CustomPasswordResetSerializer(serializers.Serializer):

    email = serializers.EmailField()
    reset_form = None

    @property
    def password_reset_form_class(self):
        return CustomPasswordResetForm

    def get_email_options(self):
        return {}

    def validate_email(self, value):
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)
        return value

    def save(self):
        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account.forms import default_token_generator
        else:
            from django.contrib.auth.tokens import default_token_generator
            token_generator = default_token_generator

        request = self.context.get('request')
        # Set options to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
            'token_generator': default_token_generator,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)
