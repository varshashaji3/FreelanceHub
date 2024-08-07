# Generated by Django 5.0.4 on 2024-07-28 11:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    

    operations = [
        migrations.CreateModel(
            name='FreelancerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('professional_title', models.CharField(max_length=255)),
                ('experience_level', models.CharField(blank=True, max_length=50, null=True)),
                ('portfolio_link', models.URLField(blank=True, max_length=255, null=True)),
                ('education', models.TextField(blank=True, null=True)),
                ('resume', models.FileField(blank=True, null=True, upload_to='resumes/')),
                ('aadhaar_document', models.FileField(blank=True, null=True, upload_to='aadhaar/')),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
                ('skills', models.ManyToManyField(blank=True, to='administrator.skill')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
