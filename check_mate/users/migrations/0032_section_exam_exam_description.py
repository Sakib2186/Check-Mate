# Generated by Django 5.0.3 on 2024-04-02 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_section_exam_exam_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='section_exam',
            name='exam_description',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
