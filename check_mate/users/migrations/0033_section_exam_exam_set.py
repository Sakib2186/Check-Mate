# Generated by Django 5.0.3 on 2024-04-03 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_section_exam_exam_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='section_exam',
            name='exam_set',
            field=models.IntegerField(default=0),
        ),
    ]
