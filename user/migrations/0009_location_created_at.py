# Generated by Django 4.2.6 on 2023-10-28 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_rename_max_accelaration_standard_max_acceleration_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=None),
            preserve_default=False,
        ),
    ]