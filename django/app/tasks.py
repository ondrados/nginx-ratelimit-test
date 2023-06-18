from app import celery_app

from .models import TestModel


@celery_app.task()
def test_task(id):
    return TestModel.objects.get(id=id).get_data()
