from datetime import timedelta

from django.db.models import Q
from rest_framework import serializers
from .models import Company, ServiceCategory, Service, Employee, Client, Appointment, WorkSchedule
from rest_framework.serializers import ValidationError


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
        Returnează doar numele și ID-ul angajaților asociați categoriei care aparțin utilizatorului autentificat.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Filtrare pe angajați în funcție de utilizatorul autentificat
            employees = obj.employees.filter(user=request.user)
            # Returnăm doar numele și ID-ul
            return [{'id': employee.id, 'name': employee.name} for employee in employees]
        return []


class WorkScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSchedule
        fields = ['id', 'employee', 'day_of_week', 'start_time', 'end_time']

    def validate(self, data):
        """
        Verifică dacă noul program de lucru se suprapune cu unul existent.
        """
        employee = data.get("employee")
        day_of_week = data.get("day_of_week")
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time.")

        # Căutăm programările existente ale acestui angajat în aceeași zi
        overlapping_schedules = WorkSchedule.objects.filter(
            employee=employee,
            day_of_week=day_of_week
        ).exclude(id=self.instance.id if self.instance else None)  # Excludem propriul obiect dacă e o actualizare

        for schedule in overlapping_schedules:
            if (schedule.start_time <= start_time < schedule.end_time) or \
               (schedule.start_time < end_time <= schedule.end_time) or \
               (start_time <= schedule.start_time and end_time >= schedule.end_time):
                raise serializers.ValidationError("This employee's schedule overlaps with an existing entry.")

        return data


class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    service_categories = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(),
        many=True
    )
    service_category_names = serializers.SerializerMethodField()
    work_schedules = WorkScheduleSerializer(many=True, read_only=True)  # Adăugăm programul de lucru

    class Meta:
        model = Employee
        fields = ['id', 'user', 'name', 'service_categories', 'service_category_names', 'work_schedules']

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
            'employee', 'employee_id', 'date', 'end_date', 'status', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        """
        Validate overlapping appointments for the same employee.
        """
        date = data.get('date')
        service = data.get('service')
        employee = data.get('employee')

        if date and service and employee:
            service_duration = service.time  # Duration in minutes
            start_time = date
            end_time = start_time + timedelta(minutes=service_duration)

            # Check for overlapping appointments
            overlapping_appointments = Appointment.objects.filter(
                employee=employee
            ).filter(
                Q(date__lt=end_time, end_date__gt=start_time)
            )

            # Exclude current instance in case of update
            if self.instance:
                overlapping_appointments = overlapping_appointments.exclude(pk=self.instance.pk)

            if overlapping_appointments.exists():
                # Get details of the conflicting appointment
                conflicting_appointment = overlapping_appointments.first()
                conflicting_start = conflicting_appointment.date
                conflicting_end = conflicting_appointment.end_date

                raise ValidationError({
                    'date': (
                        f"{employee.name} is already booked between "
                        f"{conflicting_start.strftime('%Y-%m-%d %H:%M:%S')} and "
                        f"{conflicting_end.strftime('%Y-%m-%d %H:%M:%S')}. "
                        "Please choose another time."
                    )
                })

        return data
