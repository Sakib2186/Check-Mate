# Generated by Django 5.0.3 on 2024-04-03 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='question_set',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
