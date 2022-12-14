# Generated by Django 3.2.13 on 2022-08-10 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsWeb', '0005_movies'),
    ]

    operations = [
        migrations.CreateModel(
            name='rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('rate', models.IntegerField(default=10)),
                ('username', models.CharField(max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='movies',
            name='id',
        ),
        migrations.AlterField(
            model_name='movies',
            name='title',
            field=models.CharField(max_length=200, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='movies',
            name='year',
            field=models.IntegerField(default=2000),
        ),
    ]
