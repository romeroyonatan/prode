# Generated by Django 2.0.5 on 2018-05-17 12:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('apuestas', '0004_auto_20180517_1222'),
    ]

    operations = [
        migrations.AddField(
            model_name='partido',
            name='fecha',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
