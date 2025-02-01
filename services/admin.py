from django.contrib import admin
from .models import Company, ServiceCategory, Service, Employee, Client, Appointment, WorkSchedule, LeaveDay


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'slug')
    search_fields = ('name', 'user__username')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'service_category', 'time')
    search_fields = ('name', 'user__username', 'service_category__name')
    list_filter = ('service_category',)


# Inline admin pentru LeaveDay
class LeaveDayInline(admin.TabularInline):
    model = LeaveDay
    extra = 1


# Inline admin pentru WorkSchedule
class WorkScheduleInline(admin.TabularInline):  # Sau StackedInline pentru un stil diferit
    model = WorkSchedule
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
    filter_horizontal = ('service_categories',)
    inlines = [WorkScheduleInline, LeaveDayInline]  # Adaugă programul de lucru inline


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'user')
    search_fields = ('name', 'email', 'user__username')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'employee', 'date', 'end_date', 'status', 'created_at')
    search_fields = ('client__name', 'service__name', 'employee__name')
    list_filter = ('status', 'date')
    ordering = ['date']


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ('employee', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'employee')
    search_fields = ('employee__name', 'day_of_week')
    ordering = ('employee', 'day_of_week')


@admin.register(LeaveDay)
class LeaveDayAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date')
    list_filter = ('employee', 'date')
    search_fields = ('employee__name',)
    ordering = ('employee', 'date')