# Generated by Django 5.1.6 on 2025-03-06 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendor", "0002_location"),
    ]

    operations = [
        migrations.DeleteModel(name="Location",),
        migrations.AddField(
            model_name="vendor",
            name="vendor_slug",
            field=models.SlugField(blank=True, max_length=100),
        ),
    ]
