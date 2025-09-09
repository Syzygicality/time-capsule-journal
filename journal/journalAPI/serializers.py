from rest_framework import serializers
from .models import User, Capsule, Draft
from utilities.encryption import encrypt_message, decrypt_message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "phone_number"]

class CapsuleSerializer(serializers.ModelSerializer):
    message = serializers.CharField(write_only=True)
    decrypted_message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Capsule
        fields = ["capsule_id", "message", "decrypted_message", "creation_date", "release_date"]

    def create(self, validated_data):
        raw_message = validated_data.pop("message")
        validated_data["encrypted_message"] = encrypt_message(raw_message)
        return super().create(validated_data)
    
    def get_decrypted_message(self, capsule):
        return decrypt_message(capsule.encrypted_message)


class DraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Draft
        fields = ["message", "locked_time", "creation_date", "modified_date"]
    