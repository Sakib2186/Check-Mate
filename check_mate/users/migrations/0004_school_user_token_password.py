# Generated by Django 5.0.3 on 2024-03-15 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_school_users_user_profile_picture_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='school_user_token',
            name='password',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
    ]
