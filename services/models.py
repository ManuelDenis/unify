from django.db import models
from django.utils.text import slugify
from unify import settings
from users.models import CustomUser
from datetime import timedelta


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_category_within_user')
        ]

    def save(self, *args, **kwargs):
        # Capitalize the first letter of each word in the name
        self.name = self.name.title()
        super().save(*args, **kwargs)


class Service(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', null=True, blank=True)
    name = models.CharField(max_length=150)
    time = models.IntegerField(default=0)
    slug = models.SlugField(max_length=255, blank=True)

    class Meta:
        ordering = ['name']

    constraints = [
        models.UniqueConstraint(fields=['service_category', 'name'], name='unique_service_within_category')
    ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Service, self).save(*args, **kwargs)


class Employee(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    service_categories = models.ManyToManyField(ServiceCategory, related_name='employees', blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Capitalize the first letter of each word in the name
        self.name = self.name.title()
        super().save(*args, **kwargs)


class WorkSchedule(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='work_schedules')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)  # Schimbăm în IntegerField pentru a stoca numere
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    class Meta:
        # Folosim day_of_week pentru ordonare
        ordering = ['employee', 'day_of_week']

    def __str__(self):
        start = self.start_time if self.start_time else "Not set"
        end = self.end_time if self.end_time else "Not set"
        return f"{self.employee.name} - {self.get_day_of_week_display()}: {start} to {end}"


class LeaveDay(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='leave_days')
    date = models.DateField(help_text="Date of leave when no appointments can be scheduled.")

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.name} - Leave on {self.date}"


class Client(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()

    class Meta:
        unique_together = ('name', 'email')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Capitalize the first letter of each word in the name
        self.name = self.name.title()
        super().save(*args, **kwargs)


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
    date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS, default='scheduled')

    class Meta:
        unique_together = ('client', 'service', 'employee', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.client.name} - {self.service.name} with {self.employee.name} on {self.date}"

    def save(self, *args, **kwargs):
        # Automatically set end_date based on service duration
        if self.date and self.service:
            self.end_date = self.date + timedelta(minutes=self.service.time)

        # Run the clean method to validate data
        self.clean()
        super(Appointment, self).save(*args, **kwargs)
