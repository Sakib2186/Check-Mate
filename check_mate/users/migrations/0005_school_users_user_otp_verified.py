# Generated by Django 5.0.3 on 2024-03-15 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_school_user_token_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='school_users',
            name='user_otp_verified',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]