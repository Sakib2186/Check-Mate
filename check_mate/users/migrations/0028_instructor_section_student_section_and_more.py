# Generated by Django 5.0.3 on 2024-03-30 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_alter_instructor_courses_alter_student_courses_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructor',
            name='section',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='student',
            name='section',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='teaching_assistant',
            name='section',
            field=models.IntegerField(default=1),
        ),
    ]
