# Generated by Django 5.0.4 on 2024-08-16 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0003_repository_sharedfile_sharednote_sharedurl'),
    ]

    operations = [
        migrations.AddField(
            model_name='sharedfile',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]