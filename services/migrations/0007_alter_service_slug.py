# Generated by Django 5.1 on 2024-12-23 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_alter_service_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='slug',
            field=models.SlugField(blank=True, max_length=255),
        ),
    ]
