# Generated by Django 3.2.13 on 2022-08-11 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsWeb', '0009_push'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='like',
            field=models.FloatField(default=0),
        ),
    ]