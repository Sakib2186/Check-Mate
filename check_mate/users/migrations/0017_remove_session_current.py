# Generated by Django 5.0.3 on 2024-03-25 07:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_course_section_semester_alter_instructor_semester_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='current',
        ),
    ]
