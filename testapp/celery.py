from celery import Celery

app = Celery("nrc")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
