# Generated by Django 5.1.6 on 2025-03-18 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_order_total_tax"),
        ("vendor", "0006_alter_openinghour_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="total_data",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="vendors",
            field=models.ManyToManyField(blank=True, to="vendor.vendor"),
        ),
    ]
