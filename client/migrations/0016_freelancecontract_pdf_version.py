# Generated by Django 5.0.4 on 2024-08-30 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0015_project_gst_amount_project_gst_rate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='freelancecontract',
            name='pdf_version',
            field=models.FileField(blank=True, null=True, upload_to='contracts/pdf/'),
        ),
    ]
