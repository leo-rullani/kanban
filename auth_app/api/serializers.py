from rest_framework import serializers
from auth_app.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.
    Includes password validation and full name.
    """
    password = serializers.CharField(write_only=True, required=True)
    repeated_password = serializers.CharField(write_only=True, required=True)
    fullname = serializers.CharField(source="full_name", required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "fullname",
            "email",
            "password",
            "repeated_password",
            "date_joined",
            "is_active",
        ]
        read_only_fields = ["id", "date_joined", "is_active"]

    def validate(self, data):
        """
        Checks if both passwords match during registration.
        """
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        """
        Creates a new user with a hashed password and full name.
        """
        full_name = validated_data.pop("full_name", "")
        email = validated_data.get("email")
        password = validated_data.pop("password")
        validated_data.pop("repeated_password", None)
        user = User(email=email, full_name=full_name)
        user.set_password(password)
        user.save()
        return user
