# backend/app/celery_app.py

import os
from celery import Celery
import logging

# Set up logging for Celery
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Redis URL from environment variable
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
if not REDIS_URL:
    logger.error("REDIS_URL environment variable is not set for Celery.")
    raise ValueError("REDIS_URL environment variable is not set for Celery.")

# Initialize Celery application
# The 'celery' variable name here is what the 'celery -A app.celery_app worker' command expects.
celery = Celery(
    'abparts_celery_app',
    broker=REDIS_URL,
    backend=REDIS_URL, # Using Redis for backend to store task results
    include=['app.tasks'] # Specify where your tasks will be located
)

# Optional: Configure Celery if needed (e.g., timezone)
celery.conf.update(
    task_track_started=True,
    task_time_limit=300, # Max time a task can run
    broker_connection_retry_on_startup=True,
    timezone='Europe/Lisbon', # Based on your current location
    enable_utc=True,
)

# Example task (you'll define more complex tasks in app/tasks.py)
@celery.task
def debug_task(name):
    """
    A simple task to demonstrate Celery functionality.
    """
    logger.info(f"Running debug task for: {name}")
    return f"Debug task completed for {name}"

# You can also set up a periodic task for the recommendation engine later
# For example:
# @celery.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Calls update_recommendations every day at midnight
#     sender.add_periodic_task(
#         crontab(minute=0, hour=0),
#         update_recommendations.s(),
#         name='update minimum stock recommendations daily'
#     )

# Placeholder for your actual ML recommendation task
# (This task would be defined in app/tasks.py and imported if necessary)
# @celery.task
# def update_recommendations():
#     logger.info("Running update_recommendations task...")
#     # Add your ML logic here to fetch data, train model, update inventory minimums
#     pass
