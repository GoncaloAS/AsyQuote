# Generated by Django 4.2.6 on 2023-11-07 15:36

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):
    dependencies = [
        ("landingpage", "0009_reviewhome_homepage_review_title_customimage"),
    ]

    operations = [
        migrations.AddField(
            model_name="reviewhome",
            name="page",
            field=modelcluster.fields.ParentalKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="review_home",
                to="landingpage.homepage",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="reviewhome",
            name="review_card",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="review_homes",
                to="landingpage.customimage",
            ),
        ),
    ]