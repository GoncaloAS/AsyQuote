# Generated by Django 4.2.6 on 2023-11-09 16:34

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):
    dependencies = [
        ("landingpage", "0014_homepage_hero_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="footer_navigation_title",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.CreateModel(
            name="FooterNavigation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                ("navigation_text", models.CharField(blank=True, max_length=255, null=True)),
                ("navigation_url", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="footer_navigation",
                        to="landingpage.homepage",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
