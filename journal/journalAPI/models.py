from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)

class Capsule(models.Model):
    capsule_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(User, on_delete=models.CASCADE)
    message = models.TextField(blank=False, null=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    locked_time = models.DurationField(blank=False, null=False)