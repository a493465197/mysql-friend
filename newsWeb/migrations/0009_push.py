# Generated by Django 3.2.13 on 2022-08-10 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsWeb', '0008_users_like_movies_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='push',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('pusername', models.CharField(max_length=200)),
                ('time', models.CharField(default='', max_length=200)),
            ],
        ),
    ]
