# Generated by Django 4.2.6 on 2023-11-10 12:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("landingpage", "0020_homepage_faqs_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="footercontact",
            name="information_url",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]