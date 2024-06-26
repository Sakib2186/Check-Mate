# Generated by Django 5.0.3 on 2024-03-25 05:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_course_course_description_course_course_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courses', models.ManyToManyField(related_name='instructor_courses', to='users.course')),
                ('instructor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instructor_id', to='users.school_users')),
            ],
            options={
                'verbose_name': 'Instructor Courses',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courses', models.ManyToManyField(to='users.course')),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.school_users')),
            ],
            options={
                'verbose_name': 'Student Courses',
            },
        ),
    ]
