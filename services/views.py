from .models import Company, Service, Employee, Client, Appointment, WorkSchedule
from .serializers import CompanySerializer, ServiceSerializer, EmployeeSerializer, ClientSerializer, \
    AppointmentSerializer, WorkScheduleSerializer
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import ServiceCategory
from .serializers import ServiceCategorySerializer


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


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returnează serviciile asociate utilizatorului autentificat.
        """
        return Service.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Creează un nou serviciu, setând automat utilizatorul curent ca proprietar.
        Permite crearea unui serviciu doar dacă este unic în categoria respectivă pentru utilizator.
        """
        # Extract category and name from the serializer's validated data
        category = serializer.validated_data.get('service_category')
        name = serializer.validated_data.get('name')

        # Check if a service with the same name already exists in the same category for the user
        existing_service = Service.objects.filter(
            user=self.request.user,
            service_category=category,
            name=name
        )

        if existing_service.exists():
            raise ValidationError(
                "A service with this name already exists in the selected category for this user."
            )

        # Save the new service with the current user
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Permite doar utilizatorului autentic să își actualizeze propriul serviciu,
        dacă numele actualizat este unic în categoria respectivă.
        """
        instance = self.get_object()

        # Ensure the service belongs to the authenticated user
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this service.")

        # Extract the new name and category (or keep the current ones if not being updated)
        new_name = serializer.validated_data.get('name', instance.name)
        new_category = serializer.validated_data.get('service_category', instance.service_category)

        # Check if there's another service with the same name in the same category
        conflicting_service = Service.objects.filter(
            user=self.request.user,
            service_category=new_category,
            name=new_name
        ).exclude(pk=instance.pk)  # Exclude the current instance

        if conflicting_service.exists():
            raise ValidationError(
                "A service with this name already exists in the selected category for this user."
            )

        # Save the updated service
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Permite doar utilizatorului autentic să șteargă propriul serviciu.
        """
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this service.")
        return super().destroy(request, *args, **kwargs)


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returnează doar categoriile create de utilizatorul autentificat.
        """
        return ServiceCategory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Creează o nouă categorie de serviciu, setând automat utilizatorul curent ca proprietar.
        """
        if ServiceCategory.objects.filter(user=self.request.user, name=serializer.validated_data['name']).exists():
            raise PermissionDenied("You already have a category with this name")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Permite doar utilizatorului autentic să își actualizeze categoria de serviciu.
        """
        instance = self.get_object()

        # Verificăm dacă utilizatorul este proprietarul categoriei
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this category.")

        # Verificăm dacă există o altă categorie cu același nume
        new_name = serializer.validated_data.get('name')
        if ServiceCategory.objects.filter(user=self.request.user, name=new_name).exclude(id=instance.id).exists():
            raise ValidationError({"detail": "You already have a category with this name."})

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Permite doar utilizatorului autentic să șteargă propria categorie de serviciu.
        """
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this category.")
        return super().destroy(request, *args, **kwargs)


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returnează doar angajații care aparțin utilizatorului autentificat.
        """
        return Employee.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Creează un nou angajat și setează automat utilizatorul curent ca proprietar.
        """
        category = serializer.validated_data.get('service_category')
        # Verificăm dacă un angajat cu același nume există deja pentru utilizator
        name = serializer.validated_data.get('name')

        if Employee.objects.filter(user=self.request.user, name=name).exists():
            raise ValidationError("You already have an employee with this name.")

        # Salvăm angajatul asociindu-l cu utilizatorul curent
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Permite doar utilizatorului autentic să își actualizeze propriul angajat.
        """
        instance = self.get_object()

        # Verificăm dacă utilizatorul este proprietarul angajatului
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this employee.")

        # Verificăm dacă există un alt angajat cu același nume pentru utilizator
        new_name = serializer.validated_data.get('name', instance.name)
        if Employee.objects.filter(user=self.request.user, name=new_name).exclude(id=instance.id).exists():
            raise ValidationError("You already have an employee with this name.")

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Permite doar utilizatorului autentic să șteargă propriul angajat.
        """
        instance = self.get_object()

        # Verificăm dacă utilizatorul este proprietarul angajatului
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this employee.")

        return super().destroy(request, *args, **kwargs)


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returnează doar clienții asociați utilizatorului autentificat.
        """
        return Client.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Creează un nou client, setând automat utilizatorul curent ca proprietar.
        """
        # Verificăm dacă există deja un client cu același nume și email pentru utilizator
        name = serializer.validated_data.get('name')
        email = serializer.validated_data.get('email')
        if Client.objects.filter(user=self.request.user, name=name, email=email).exists():
            raise ValidationError("You already have a client with this name and email.")

        # Salvăm clientul asociindu-l cu utilizatorul curent
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Permite doar utilizatorului autentic să își actualizeze propriul client.
        """
        instance = self.get_object()

        # Verificăm dacă utilizatorul este proprietarul clientului
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this client.")

        # Verificăm dacă există un alt client cu același nume și email pentru utilizator
        new_name = serializer.validated_data.get('name', instance.name)
        new_email = serializer.validated_data.get('email', instance.email)
        if Client.objects.filter(user=self.request.user, name=new_name, email=new_email).exclude(id=instance.id).exists():
            raise ValidationError("You already have a client with this name and email.")

        # Salvăm actualizările
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Permite doar utilizatorului autentic să șteargă propriul client.
        """
        instance = self.get_object()

        # Verificăm dacă utilizatorul este proprietarul clientului
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this client.")

        return super().destroy(request, *args, **kwargs)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return only appointments belonging to the authenticated user.
        """
        return Appointment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        print("Data received:", serializer.validated_data)  # Log pentru verificare
        """
        Create a new appointment for the authenticated user, ensuring uniqueness constraints are respected.
        """
        client = serializer.validated_data.get('client')
        service = serializer.validated_data.get('service')
        employee = serializer.validated_data.get('employee')
        date = serializer.validated_data.get('date')

        # Check for conflicting appointments
        if Appointment.objects.filter(
            client=client,
            user=self.request.user,
            service=service,
            employee=employee,
            date=date
        ).exists():
            raise ValidationError("An appointment with this service, employee, and date already exists.")

        # Save the new appointment
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Update an appointment for the authenticated user, respecting ownership and uniqueness constraints.
        """
        instance = self.get_object()

        # Ensure the appointment belongs to the authenticated user
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this appointment.")

        # Check for conflicting appointments
        new_service = serializer.validated_data.get('service', instance.service)
        new_employee = serializer.validated_data.get('employee', instance.employee)
        new_date = serializer.validated_data.get('date', instance.date)

        if Appointment.objects.filter(
            user=self.request.user,
            service=new_service,
            employee=new_employee,
            date=new_date
        ).exclude(pk=instance.pk).exists():
            raise ValidationError("An appointment with this service, employee, and date already exists.")

        # Save the updated appointment
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Allow only the authenticated user to delete their appointments.
        """
        instance = self.get_object()

        # Ensure the appointment belongs to the authenticated user
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this appointment.")

        return super().destroy(request, *args, **kwargs)


class WorkScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = WorkScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returnăm programele de lucru asociate utilizatorului autentificat.
        """
        user = self.request.user
        return WorkSchedule.objects.filter(user=user).select_related('employee')

    def perform_create(self, serializer):
        """
        Setăm utilizatorul autentificat ca proprietar al programului de lucru.
        """
        serializer.save(user=self.request.user)
