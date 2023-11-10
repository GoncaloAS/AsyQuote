# Generated by Django 4.2.6 on 2023-11-05 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
        ("landingpage", "0006_homepage_hero_paragraph_homepage_hero_title_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="logo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.DeleteModel(
            name="Navbar",
        ),
    ]