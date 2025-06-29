from django.contrib.auth.hashers import make_password  # Import hasher
from rest_framework import serializers

from .models import (
    ClubMemberProfile,
    FacultyAdvisorProfile,
    Permission,
    Role,
    RolePermission,
    SecurityHeadProfile,
    StudentCouncilProfile,
    StudentWelfareProfile,
    User,
    UserRole,
)


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"  # Include all fields from the model


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True, required=False, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["username", "email", "role", "password", "name"]
        read_only_fields = ["id"]

    def validate_username(self, value):
        user_id = self.instance.id if self.instance else None
        if User.objects.exclude(id=user_id).filter(username=value).exists():
            raise serializers.ValidationError("user with this username already exists.")
        return value

    def validate_registration_id(self, value):
        user_id = self.instance.id if self.instance else None
        if User.objects.exclude(id=user_id).filter(registration_id=value).exists():
            raise serializers.ValidationError(
                "user with this registration id already exists."
            )
        return value

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data.get("password"))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            raise serializers.ValidationError(
                {"password": "Password cannot be updated from this endpoint."}
            )
        return super().update(instance, validated_data)


# serializers.py
class ClubMemberProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubMemberProfile
        fields = "__all__"


class StudentCouncilProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCouncilProfile
        fields = "__all__"


class FacultyAdvisorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacultyAdvisorProfile
        fields = "__all__"


class StudentWelfareProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentWelfareProfile
        fields = "__all__"


class SecurityHeadProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityHeadProfile
        fields = "__all__"


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = "__all__"


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = "__all__"
