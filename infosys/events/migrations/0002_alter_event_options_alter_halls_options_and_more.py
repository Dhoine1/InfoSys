# Generated by Django 4.2.5 on 2023-09-06 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'verbose_name': 'Мероприятие', 'verbose_name_plural': 'Мероприятия'},
        ),
        migrations.AlterModelOptions(
            name='halls',
            options={'verbose_name': 'Зал', 'verbose_name_plural': 'Залы'},
        ),
        migrations.AddField(
            model_name='halls',
            name='hall_name_eng',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='logo',
            field=models.FilePathField(null=True, path='images/', verbose_name='Logo'),
        ),
    ]