# Generated by Django 5.0.3 on 2024-03-29 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_course_section_year_instructor_year_student_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instructor',
            name='courses',
            field=models.ManyToManyField(to='users.course'),
        ),
    ]
