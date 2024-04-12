# Generated by Django 5.0.3 on 2024-03-29 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_alter_instructor_courses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instructor',
            name='courses',
            field=models.ManyToManyField(blank=True, null=True, to='users.course'),
        ),
        migrations.AlterField(
            model_name='student',
            name='courses',
            field=models.ManyToManyField(blank=True, null=True, to='users.course'),
        ),
        migrations.AlterField(
            model_name='teaching_assistant',
            name='courses',
            field=models.ManyToManyField(blank=True, null=True, to='users.course'),
        ),
    ]