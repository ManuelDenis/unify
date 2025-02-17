"""
URL configuration for unify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView
from rest_framework.routers import DefaultRouter
from services.views import CompanyViewSet, ServiceCategoryViewSet, ServiceViewSet, EmployeeViewSet, ClientViewSet, \
    AppointmentViewSet, WorkScheduleViewSet

router = DefaultRouter()
router.register('company', CompanyViewSet, basename='company')
router.register('service_category', ServiceCategoryViewSet, basename='service_category')
router.register('services', ServiceViewSet, basename='services')
router.register('employees', EmployeeViewSet, basename='employees')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'appointments', AppointmentViewSet, basename='appointments')
router.register(r'workschedule', WorkScheduleViewSet, basename='workschedule')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('api/', include(router.urls)),
    path('services/', include('services.urls')),
    path('password-reset/', PasswordResetView.as_view()),  # Folosește vizualizarea personalizată
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
