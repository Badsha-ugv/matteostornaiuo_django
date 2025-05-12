
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')  # Replace with your project name

app = Celery('project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# Create your tasks here. For example:
app.conf.beat_schedule = {
    'daily-2pm-task': {
        'task': 'client.tasks.print_hello',
        # 'schedule': crontab(hour=14, minute=54),
        'schedule': crontab(), 
    },
    'daily-update-job-task': {
        'task': 'client.tasks.update_job_status',
        # 'schedule': crontab(hour=14, minute=54),
        'schedule': crontab(hour=17,minute=42),  
    },
    

}