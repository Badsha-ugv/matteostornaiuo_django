# Generated by Django 5.1.4 on 2025-02-12 05:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0010_jobapplication_checkin_approve_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jobapplication',
            old_name='checout_location',
            new_name='checkout_location',
        ),
    ]
