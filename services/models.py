from django.db import models
from django.utils.text import slugify
from unify import settings
from users.models import CustomUser


class Company(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Company, self).save(*args, **kwargs)


class ServiceCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=150, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    service_categories = models.ManyToManyField(ServiceCategory, related_name='employees', blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Client(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()

    class Meta:
        unique_together = ('name', 'email')
        ordering = ['name']

    def __str__(self):
        return self.name


APPOINTMENT_STATUS = [
    ('scheduled', 'Scheduled'),
    ('confirmed', 'Confirmed'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]


class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='appointments')
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='appointments')
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS, default='scheduled')

    class Meta:
        unique_together = ('service', 'employee', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.client.name} - {self.service.name} with {self.employee.name} on {self.date}"
