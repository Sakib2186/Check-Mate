# Generated by Django 5.0.3 on 2024-04-13 15:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0055_remove_answer_is_uploaded_exam_submitted'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exam_submitted',
            options={'verbose_name': 'Exam Submitted'},
        ),
    ]
