from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    phone_number = PhoneNumberField()

class Capsule(models.Model):
    capsule_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(blank=False, null=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    release_date = models.DateTimeField()

class Draft(models.Model):
    draft_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.ForeignKey(Capsule, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField()
    locked_time = models.DurationField()