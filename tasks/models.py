from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Task(models.Model):
    NEW = 0
    DONE = 1

    TASK_STATUS = {NEW, DONE}

    name = models.CharField(max_length=256, null=False)
    description = models.TextField(null=False)
    status = models.IntegerField(
        default=NEW
    )  # Числовий тип, для потенційного збільшення кількості станів
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="tasks", null=True
    )
