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

    # Map user roles to profile models and serializers
    profile_map = {
        "clubMember": ClubMemberProfileSerializer,
        "studentCouncil": StudentCouncilProfileSerializer,
        "facultyAdvisor": FacultyAdvisorProfileSerializer,
        "studentWelfare": StudentWelfareProfileSerializer,
        "securityHead": SecurityHeadProfileSerializer,
    }

    for user in all_users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "registration_id": user.registration_id,
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

        # Try to get related profile based on user type
        try:
            role_key = user.role.name  # e.g., "clubMember"
            serializer_class = profile_map.get(role_key)
            if serializer_class:
                profile_instance = getattr(user, f"{role_key}_profile", None)
                if profile_instance:
                    user_data["profile"] = serializer_class(profile_instance).data
        except Exception as e:
            print(f"⚠️ Error fetching profile for user {user.username}: {e}")
            user_data["profile"] = None

        all_users_data.append(user_data)

    return JsonResponse(all_users_data, safe=False, status=200)


@session_login_required
@check_user_permission([{"subject": "user", "action": "update"}])
def update_user(request):
    if request.method != "PUT":
        return JsonResponse({"error": "Only PUT method allowed."}, status=405)

    try:
        body = json.loads(request.body)
        user_type = request.GET.get("type")
        print("type : ", user_type)
        user_id = body.get("id")

        if not user_id:
            return JsonResponse({"error": "User ID is required."}, status=400)

        # ❌ Block if password is present
        if "password" in body:
            return JsonResponse(
                {"error": "Password cannot be updated from this endpoint."}, status=400
            )

        user = User.objects.get(id=user_id)

        # Update core User fields
        user_serializer = UserSerializer(user, data=body)
        if not user_serializer.is_valid():
            return JsonResponse(user_serializer.errors, status=400)
        user_serializer.save()

        print("user : ", user_serializer.data)

        # Determine correct profile serializer
        profile_serializer_map = {
            "clubMember": ClubMemberProfileSerializer,
            "studentCouncil": StudentCouncilProfileSerializer,
            "facultyAdvisor": FacultyAdvisorProfileSerializer,
            "studentWelfare": StudentWelfareProfileSerializer,
            "securityHead": SecurityHeadProfileSerializer,
        }

        ProfileSerializer = profile_serializer_map.get(user_type)
        if not ProfileSerializer:
            return JsonResponse({"error": "Invalid user type"}, status=400)

        # Update profile
        profile_model_map = {
            "clubMember": "clubmemberprofile",
            "studentCouncil": "studentcouncilprofile",
            "facultyAdvisor": "facultyadvisorprofile",
            "studentWelfare": "studentwelfareprofile",
            "securityHead": "securityheadprofile",
        }

        profile_attr = profile_model_map.get(user_type)
        profile_instance = getattr(user, profile_attr, None)

        print("profile_instance : ", profile_instance)
        if not profile_instance:
            return JsonResponse(
                {"error": f"No profile found for user type '{user_type}'."}, status=404
            )

        profile_data = body.get("profile", {})
        profile_serializer = ProfileSerializer(
            profile_instance, data=profile_data, partial=True
        )

        if profile_serializer.is_valid():
            profile_serializer.save()
        else:
            return JsonResponse(profile_serializer.errors, status=400)

        # Combine response
        return JsonResponse(
            {"user": user_serializer.data, "profile": profile_serializer.data},
            status=200,
        )

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        print("🔥 Error during user update:", str(e))
        return JsonResponse({"error": "Internal server error."}, status=500)


@session_login_required
@check_user_permission([{"subject": "user", "action": "delete"}])
def delete_user(request):
    try:
        body = json.loads(request.body)
        user_id = int(body.get("id"))
        user = User.objects.get(id=user_id)
        print("🗑️ Deleting user:", user.username)

        # Map user types to profile model attribute names
        profile_model_map = {
            "clubMember": "clubmemberprofile",
            "studentCouncil": "studentcouncilprofile",
            "facultyAdvisor": "facultyadvisorprofile",
            "studentWelfare": "studentwelfareprofile",
            "securityHead": "securityheadprofile",
        }

        # Try to detect and delete the user's profile
        for key, attr in profile_model_map.items():
            profile = getattr(user, attr, None)
            if profile:
                print(f"🗑️ Deleting profile: {attr}")
                profile.delete()
                break  # Assuming one user has only one profile

        # Delete the user itself
        user.delete()

        return JsonResponse(
            {"message": "User and profile deleted successfully"}, status=200
        )

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        print("🔥 Error during user deletion:", str(e))
        return JsonResponse({"error": "Internal server error."}, status=500)


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
