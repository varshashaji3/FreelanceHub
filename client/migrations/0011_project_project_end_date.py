# Generated by Django 5.0.4 on 2024-08-28 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0010_paymentinstallment_razorpay_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_end_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]