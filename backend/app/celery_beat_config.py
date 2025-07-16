# backend/app/celery_beat_config.py
"""
Celery Beat configuration for periodic tasks
"""

from celery.schedules import crontab

# Celery Beat schedule configuration
beat_schedule = {
    'cleanup-expired-invitations': {
        'task': 'app.tasks.cleanup_expired_invitations',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2:00 AM
        'options': {'queue': 'default'}
    },
}

# Timezone for the scheduler
timezone = 'UTC'