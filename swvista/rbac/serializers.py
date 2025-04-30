from django.contrib.auth.hashers import make_password  # Import hasher
from rest_framework import serializers

from .models import Permission, Role, RolePermission, User, UserRole


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"  # Include all fields from the model


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    # Make password write-only
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        # Add 'password' to fields used for input, but it won't be in output due to write_only=True
        fields = ["username", "email", "role", "password", "name", "registration_id"]
        read_only_fields = ["id"]  # Make id read-only

    def create(self, validated_data):
        # Hash password before creating user
        validated_data["password"] = make_password(validated_data.get("password"))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Hash password if it is being updated
        password = validated_data.pop("password", None)
        if password:
            instance.password = make_password(password)
        # Update other fields as usual
        return super().update(instance, validated_data)


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = "__all__"


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = "__all__"
