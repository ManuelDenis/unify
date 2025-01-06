from rest_framework import serializers
from .models import Company, ServiceCategory, Service, Employee, Client, Appointment


class CompanySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Company
        fields = ['id', 'user', 'name', 'slug']


class ServiceSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    service_category = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all()
    )

    class Meta:
        model = Service
        fields = ['id', 'name', 'user', 'service_category']


class ServiceCategorySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    services = serializers.SerializerMethodField()
    employees = serializers.SerializerMethodField()

    class Meta:
        model = ServiceCategory
        fields = ['id', 'user', 'name', 'services', 'employees']

    def get_services(self, obj):
        """
        Returnează doar serviciile asociate categoriei care aparțin utilizatorului autentificat.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return ServiceSerializer(
                obj.services.filter(user=request.user),  # Filtrare pe utilizatorul autentificat
                many=True
            ).data
        return []

    def get_employees(self, obj):
        """
        Returnează doar angajații asociați categoriei care aparțin utilizatorului autentificat.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Filtrare pe angajați în funcție de utilizatorul autentificat
            employees = obj.employees.filter(user=request.user)
            return EmployeeSerializer(employees, many=True).data
        return []


class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    service_categories = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(),
        many=True
    )
    service_category_names = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'user', 'name', 'service_categories', 'service_category_names']

    def get_service_category_names(self, obj):
        # Returnăm lista de nume ale categoriilor
        return [category.name for category in obj.service_categories.all()]


class ClientSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Client
        fields = ['id', 'user', 'name', 'email']


class AppointmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source='client',
        write_only=True
    )
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source='service',
        write_only=True
    )
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            'id', 'user', 'client', 'client_id', 'service', 'service_id',
            'employee', 'employee_id', 'date', 'status', 'created_at', 'updated_at'
        ]
