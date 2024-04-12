# Generated by Django 4.2.6 on 2024-03-08 17:43

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0004_alter_mypage_body"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mypage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    (
                        "title",
                        wagtail.blocks.StructBlock(
                            [
                                ("name", wagtail.blocks.CharBlock()),
                                (
                                    "items",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                ("name", wagtail.blocks.CharBlock()),
                                                (
                                                    "prices",
                                                    wagtail.blocks.ListBlock(
                                                        wagtail.blocks.StructBlock(
                                                            [
                                                                ("cost", wagtail.blocks.DecimalBlock()),
                                                                ("price", wagtail.blocks.DecimalBlock()),
                                                            ]
                                                        )
                                                    ),
                                                ),
                                            ]
                                        )
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                use_json_field=True,
            ),
        ),
    ]
