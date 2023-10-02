# Generated by Django 4.2.5 on 2023-09-13 09:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_alter_event_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='room',
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
                ('hall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.halls')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='room',
            field=models.ManyToManyField(through='events.Location', to='events.halls', verbose_name='Зал'),
        ),
    ]