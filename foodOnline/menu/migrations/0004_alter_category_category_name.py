# Generated by Django 5.1.6 on 2025-03-10 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0003_alter_fooditem_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="category_name",
            field=models.CharField(max_length=50),
        ),
    ]
