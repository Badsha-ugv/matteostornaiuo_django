# Generated by Django 5.1.4 on 2025-01-26 05:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('client', '0001_initial'),
        ('staff', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyShift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('location', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.staff')),
            ],
            options={
                'verbose_name_plural': 'Daily Shifts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Shifting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client.companyprofile')),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shifting.dailyshift')),
                ('shift_for', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='client.mystaff')),
            ],
            options={
                'verbose_name_plural': 'Shifts',
                'ordering': ['-created_at'],
                'unique_together': {('company', 'shift_for')},
            },
        ),
    ]
