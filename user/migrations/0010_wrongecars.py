# Generated by Django 4.2.6 on 2023-10-29 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_location_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='WrongeCars',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('script', models.CharField(max_length=255)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='out_of_range', to='user.company')),
            ],
        ),
    ]