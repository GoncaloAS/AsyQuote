# Generated by Django 4.2.6 on 2023-11-09 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
        ("landingpage", "0013_homepage_action_benefit_homepage_action_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="hero_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
    ]