# Generated by Django 5.0.4 on 2024-07-28 11:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('client_type', models.CharField(choices=[('Individual', 'Individual'), ('Company', 'Company')], default='Individual', max_length=50)),
                ('company_name', models.CharField(blank=True, max_length=255, null=True)),
                ('website', models.URLField(blank=True, max_length=255, null=True)),
                ('license_number', models.CharField(blank=True, max_length=255, null=True)),
                ('aadhaar_document', models.FileField(blank=True, null=True, upload_to='aadhaar/')),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]