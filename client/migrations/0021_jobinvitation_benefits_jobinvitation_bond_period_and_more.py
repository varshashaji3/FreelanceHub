# Generated by Django 5.0.4 on 2025-02-04 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0020_jobinvitation_hiring_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobinvitation',
            name='benefits',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='jobinvitation',
            name='bond_period',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='jobinvitation',
            name='contract_needed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='jobinvitation',
            name='work_mode',
            field=models.CharField(choices=[('Remote', 'Remote'), ('Hybrid', 'Hybrid'), ('On-Site', 'On-Site'), ('Specify Later', 'Specify Later')], default='Specify Later', max_length=50),
        ),
    ]
