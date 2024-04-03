# Generated by Django 5.0.3 on 2024-03-26 07:48

import django.db.models.deletion
import django_resized.forms
import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_session_current'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_picture',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, null=True, quality=80, scale=1.0, size=[500, 300], upload_to=users.models.course_picture_upload_path),
        ),
        migrations.AlterField(
            model_name='course_section',
            name='instructor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.instructor'),
        ),
    ]
