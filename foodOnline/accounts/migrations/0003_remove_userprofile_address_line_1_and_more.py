# Generated by Django 5.1.6 on 2025-03-03 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_userprofile"),
    ]

    operations = [
        migrations.RemoveField(model_name="userprofile", name="address_line_1",),
        migrations.RemoveField(model_name="userprofile", name="address_line_2",),
        migrations.AddField(
            model_name="userprofile",
            name="address_line",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.PositiveSmallIntegerField(
                blank=True, choices=[(1, "Vendor"), (0, "Customer")], null=True
            ),
        ),
    ]
