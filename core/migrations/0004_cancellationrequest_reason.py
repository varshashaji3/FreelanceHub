# Generated by Django 5.0.4 on 2024-09-30 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_cancellationrequest_refundpayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='cancellationrequest',
            name='reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
