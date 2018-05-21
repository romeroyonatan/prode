# Generated by Django 2.0.5 on 2018-05-21 19:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('apuestas', '0007_auto_20180518_1525'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='etapa',
            options={'get_latest_by': 'created'},
        ),
        migrations.AddField(
            model_name='etapa',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
