from django.contrib import admin
from .models import Company, ServiceCategory, Service, Employee, Client, Appointment


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'slug')
    search_fields = ('name', 'user__username')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'service_category')
    search_fields = ('name', 'user__username', 'service_category__name')
    list_filter = ('service_category',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
    filter_horizontal = ('service_categories',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'user')
    search_fields = ('name', 'email', 'user__username')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'employee', 'date', 'status', 'created_at')
    search_fields = ('client__name', 'service__name', 'employee__name')
    list_filter = ('status', 'date')
    ordering = ['date']
