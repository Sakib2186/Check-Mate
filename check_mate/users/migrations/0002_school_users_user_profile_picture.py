# Generated by Django 5.0.3 on 2024-03-13 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='school_users',
            name='user_profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='user_profile_pictures/'),
        ),
    ]
