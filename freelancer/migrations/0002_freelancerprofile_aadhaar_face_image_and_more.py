# Generated by Django 5.0.4 on 2024-08-27 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('freelancer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='freelancerprofile',
            name='aadhaar_face_image',
            field=models.ImageField(blank=True, null=True, upload_to='aadhaar/faces/'),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='verification_attempts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='verification_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('verified', 'Verified'), ('failed', 'Failed')], default='pending', max_length=20),
        ),
    ]
