# Generated by Django 5.0.3 on 2024-04-13 15:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0054_answer_is_uploaded_delete_exam_submitted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='is_uploaded',
        ),
        migrations.CreateModel(
            name='Exam_Submitted',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_uploaded', models.BooleanField(default=False)),
                ('exam_of', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.section_exam')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.school_users')),
            ],
            options={
                'verbose_name': 'Section Exam',
            },
        ),
    ]