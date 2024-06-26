# Generated by Django 5.0.3 on 2024-03-25 06:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_instructor_semester_instructor_year_student_semester_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='course_section',
        ),
        migrations.CreateModel(
            name='Course_Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_number', models.IntegerField(default=0)),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.course')),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.instructor')),
                ('students', models.ManyToManyField(to='users.student')),
                ('teaching_assistant', models.ManyToManyField(to='users.teaching_assistant')),
            ],
            options={
                'verbose_name': 'Course Section',
            },
        ),
    ]
