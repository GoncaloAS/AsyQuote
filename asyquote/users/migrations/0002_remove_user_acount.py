# Generated by Django 4.2.6 on 2024-05-13 13:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="acount",
        ),
    ]
