# Generated by Django 5.0.3 on 2024-05-09 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0062_alter_students_score_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='students_score',
            name='total_marks',
            field=models.IntegerField(default=0),
        ),
    ]
