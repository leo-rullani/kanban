from rest_framework import serializers
from auth_app.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined', 'is_active']