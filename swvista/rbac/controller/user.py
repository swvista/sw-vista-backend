import json

from django.http import JsonResponse

from ..decorators import check_user_permission, session_login_required
from ..models import User, UserRole
from ..serializers import (
    ClubMemberProfileSerializer,
    FacultyAdvisorProfileSerializer,
    SecurityHeadProfileSerializer,
    StudentCouncilProfileSerializer,
    StudentWelfareProfileSerializer,
    UserRoleSerializer,
    UserSerializer,
)


@session_login_required
@check_user_permission([{"subject": "user", "action": "create"}])
def create_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed."}, status=405)

    try:
        body = json.loads(request.body)
        user_type = request.GET.get("type")

        print("📥 Incoming user creation request")
        print("🔍 Raw body:", json.dumps(body, indent=2))
        print("🔍 user_type query param:", user_type)

        # Validate user type
        profile_serializer_map = {
            "clubMember": ClubMemberProfileSerializer,
            "studentCouncil": StudentCouncilProfileSerializer,
            "facultyAdvisor": FacultyAdvisorProfileSerializer,
            "studentWelfare": StudentWelfareProfileSerializer,
            "securityHead": SecurityHeadProfileSerializer,
        }

        ProfileSerializer = profile_serializer_map.get(user_type)
        if not ProfileSerializer:
            print("❌ Invalid user type:", user_type)
            return JsonResponse({"error": "Invalid user type"}, status=400)

        # Create User
        user_serializer = UserSerializer(data=body)
        if not user_serializer.is_valid():
            print("❌ User serializer errors:")
            print(user_serializer.errors)
            return JsonResponse(user_serializer.errors, status=400)

        user = user_serializer.save()
        print("✅ User created successfully:", user.username)

        # Prepare and create Profile
        profile_data = body.get("profile", {})
        profile_data["user"] = user.id

        print("🔧 Profile data prepared:", json.dumps(profile_data, indent=2))

        profile_serializer = ProfileSerializer(data=profile_data)

        if profile_serializer.is_valid():
            profile_serializer.save()
            print("✅ Profile created successfully for user:", user.username)
            return JsonResponse(
                {"user": user_serializer.data, "profile": profile_serializer.data},
                status=201,
            )

        else:
            print("❌ Profile serializer errors:")
            print(profile_serializer.errors)
            # Rollback user creation
            user.delete()
            print("🧹 Rolled back user due to profile failure.")
            return JsonResponse(profile_serializer.errors, status=400)

    except json.JSONDecodeError:
        print("❌ Invalid JSON format")
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    except Exception as e:
        print("🔥 Unexpected error occurred:", str(e))
        return JsonResponse({"error": "Internal server error."}, status=500)


@session_login_required
@check_user_permission([{"subject": "user", "action": "read"}])
def get_user(request):

    all_users = User.objects.all()
    all_users_data = []
    for user in all_users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": {
                "id": user.role.id,
                "name": user.role.name,
                "description": user.role.description,
                "permissions": [
                    {"id": permission.id, "name": permission.name}
                    for permission in user.role.permissions.all()
                ],
            },
        }
        all_users_data.append(user_data)
    return JsonResponse(all_users_data, safe=False, status=200)


@session_login_required
@check_user_permission([{"subject": "user", "action": "update"}])
def update_user(request):
    body = json.loads(request.body)
    user = User.objects.get(id=body["id"])
    serializer = UserSerializer(user, data=body)
    if serializer.is_valid():
        serializer.save()
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": {
                "id": user.role.id,
                "name": user.role.name,
                "description": user.role.description,
                "permissions": [
                    {"id": permission.id, "name": permission.name}
                    for permission in user.role.permissions.all()
                ],
            },
        }
        return JsonResponse(user_data, status=200)
    return JsonResponse(serializer.errors, status=400)


@session_login_required
@check_user_permission([{"subject": "user", "action": "delete"}])
def delete_user(request):
    body = json.loads(request.body)
    user = User.objects.get(id=int(body["id"]))
    print(user)
    if user:
        user.delete()
        return JsonResponse({"message": "User deleted successfully"}, status=200)
    else:
        return JsonResponse({"message": "User not found"}, status=404)


@session_login_required
@check_user_permission([{"subject": "user", "action": "write"}])
def map_user_to_role(request):
    body = json.loads(request.body)
    print(body)
    serializer = UserRoleSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


@session_login_required
@check_user_permission([{"subject": "user", "action": "write"}])
def unmap_user_role(request):
    body = json.loads(request.body)
    print(body)
    user_role = UserRole.objects.get(id=body["id"])
    user_role.delete()
    return JsonResponse({"message": "User role deleted successfully"}, status=200)
