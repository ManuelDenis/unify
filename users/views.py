from dj_rest_auth.views import LoginView, PasswordResetConfirmView
from django.contrib.auth import get_user_model, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from .models import CustomUser  # Importă modelul tău de utilizator personalizat
from .serializers import GoogleAuthSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token  # Importă modelul Token pentru autentificare
from allauth.account.models import EmailAddress

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID


class GoogleLoginView(APIView):
    """
    View pentru autentificarea utilizatorului cu token-ul Google.
    """

    def post(self, request):
        # Validăm token-ul folosind serializer-ul
        serializer = GoogleAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Preluăm token-ul validat
        token = serializer.validated_data['token']

        try:
            # Verificăm și decodificăm token-ul
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

            # Extragem informațiile despre utilizator
            email = idinfo.get('email')
            name = idinfo.get('name')

            # Căutăm utilizatorul după `email` în loc de `username`
            user, created = CustomUser.objects.get_or_create(email=email, defaults={
                'first_name': name.split()[0],
                'last_name': " ".join(name.split()[1:]) if len(name.split()) > 1 else "",
            })

            # Dacă utilizatorul este creat nou, setăm parola și creăm o înregistrare de e-mail verificată
            if created:
                user.set_password(settings.SECRET_KEY)
                user.save()

                # Adăugăm adresa de e-mail ca verificată
                EmailAddress.objects.create(
                    user=user,
                    email=user.email,
                    verified=True,
                    primary=True
                )

            # Generăm token-ul de autentificare
            auth_token, _ = Token.objects.get_or_create(user=user)

            # Returnăm token-ul de autentificare către frontend
            return Response({"access_token": auth_token.key}, status=status.HTTP_200_OK)

        except ValueError:
            raise AuthenticationFailed("Token-ul Google este invalid.")


User = get_user_model()


class CustomLoginView(APIView):
    """
    Custom login view that provides helpful feedback if login fails.
    """

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"detail": "Email și parola sunt obligatorii."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Attempt to authenticate the user
        user = authenticate(request, username=email, password=password)

        if user:
            if user.is_active:
                # Generate or retrieve the token for the user
                token, _ = Token.objects.get_or_create(user=user)

                # Return the token in the response
                return Response({"access_token": token.key}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Contul este dezactivat. Contactează administratorul."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            # If authentication fails, check if the email exists in the database
            try:
                user = User.objects.get(email=email)
                return Response(
                    {"detail": "Email-ul există, dar parola este incorectă. Poți reseta parola."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            except User.DoesNotExist:
                # Email does not exist in the database
                return Response(
                    {"detail": "Email-ul nu există. Te rugăm să creezi un cont nou."},
                    status=status.HTTP_404_NOT_FOUND,
                )

