# Generated by Django 5.1.4 on 2025-04-17 11:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0010_alter_jobreport_job_application'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobreport',
            name='job_application',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_report', to='client.jobapplication'),
        ),
    ]
