# Generated by Django 4.2.6 on 2023-11-09 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
        ("landingpage", "0010_reviewhome_page_reviewhome_review_card"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customimage",
            name="images_cards",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
                verbose_name="Image",
            ),
        ),
    ]
