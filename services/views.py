from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Company
from .serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter to show only the company belonging to the logged-in user
        return Company.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the owner of the new company
        if Company.objects.filter(user=self.request.user).exists():
            raise PermissionDenied("You can only have one company.")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Ensure only the owner can update their company
        company = self.get_object()
        if company.user != self.request.user:
            raise PermissionDenied("You are not allowed to update this company.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        # Ensure only the owner can delete their company
        company = self.get_object()
        if company.user != self.request.user:
            raise PermissionDenied("You are not allowed to delete this company.")
        return super().destroy(request, *args, **kwargs)


