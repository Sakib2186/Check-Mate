# Generated by Django 5.0.3 on 2024-04-13 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0052_exam_submitted_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exam_submitted',
            name='file',
        ),
    ]
