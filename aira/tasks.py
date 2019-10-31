from django.core.cache import cache

from aira.celery import app


@app.task
def calculate_agrifield(agrifield):
    cache_key = "agrifield_{}_status".format(agrifield.id)
    cache.set(cache_key, "being processed", None)
    agrifield.execute_model()
    cache.set(cache_key, "done", None)
