# Generated by Django 5.0.3 on 2024-05-03 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0061_rename_mid_score_students_score_score_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='students_score',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
