from rest_framework import serializers
from .models import User, Capsule, Draft

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name"]

class CapsuleSerializer(serializers.ModelSerializer):
    release_date = serializers.SerializerMethodField
    
    class Meta:
        model = Capsule
        read_only_fields = ["message", "creation_date", "release_date"]
    
    def get_release_date(self, capsule):
        return capsule.creation_date + capsule.locked_time

class DraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Draft
        fields = ["message", "locked_time"]
        read_only_fields = ["creation_date", "modified_date"]
    