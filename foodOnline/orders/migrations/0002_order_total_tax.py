# Generated by Django 5.1.6 on 2025-03-14 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order", name="total_tax", field=models.FloatField(default=0.0),
        ),
    ]
