# Generated by Django 5.2.3 on 2025-06-14 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kanban_app", "0002_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="priority",
            field=models.CharField(
                choices=[
                    ("low", "Low"),
                    ("medium", "Medium"),
                    ("high", "High"),
                ],
                default="medium",
                max_length=10,
            ),
        ),
    ]
