from django.contrib import admin
from .models import User, Capsule, Draft
# Register your models here.
admin.site.register(User)
admin.site.register(Capsule)
admin.site.register(Draft)
