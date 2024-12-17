from rest_framework import serializers
from .models import Company, ServiceCategory, Service, Employee, Client, Appointment


class CompanySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Company
        fields = ['id', 'user', 'name', 'slug']


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name']


class ServiceSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    service_category = ServiceCategorySerializer(read_only=True)
    service_category_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(),
        source='service_category',
        write_only=True
    )

    class Meta:
        model = Service
        fields = ['id', 'name', 'user', 'service_category', 'service_category_id']


class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    service_categories = ServiceCategorySerializer(many=True, read_only=True)
    service_category_ids = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(),
        many=True,
        source='service_categories',
        write_only=True
    )

    class Meta:
        model = Employee
        fields = ['id', 'user', 'name', 'service_categories', 'service_category_ids']


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
