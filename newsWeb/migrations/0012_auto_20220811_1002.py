# Generated by Django 3.2.13 on 2022-08-11 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsWeb', '0011_auto_20220811_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='push',
            name='like_age',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='push',
            name='like_movies',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='push',
            name='like_movies_title',
            field=models.FloatField(default=0),
        ),
    ]