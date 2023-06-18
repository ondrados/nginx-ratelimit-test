import time

import requests
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import include, path

from celery import group

from app.tasks import test_task


def test(request):
    tasks = []
    for number in range(50):
        tasks.append(test_task.s(1))
    for number in range(50):
        tasks.append(test_task.s(2))
    for number in range(50):
        tasks.append(test_task.s(3))

    task_group = group(tasks)

    start = time.time()

    # Run the group of tasks
    result = task_group.apply_async()

    # Wait for the tasks to complete and get the results
    results = result.join()
    return JsonResponse({"time": time.time() - start})


urlpatterns = [
    path("", test),
]
