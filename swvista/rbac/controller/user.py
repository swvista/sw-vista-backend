import json

from django.http import JsonResponse

from ..decorators import check_user_permission, session_login_required
from ..models import (
    ClubMemberProfile,
    FacultyAdvisorProfile,
    SecurityHeadProfile,
    StudentCouncilProfile,
    StudentWelfareProfile,
    User,
)
from ..serializers import (
    ClubMemberProfileSerializer,
    FacultyAdvisorProfileSerializer,
    SecurityHeadProfileSerializer,
    StudentCouncilProfileSerializer,
    StudentWelfareProfileSerializer,
    UserRoleSerializer,
    UserSerializer,
)


# @check_user_permission([{"subject": "user", "action": "create"}])
def create_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed."}, status=405)

    print("POST REQUEST")
    try:
        body = json.loads(request.body)
        user_type = request.GET.get("type")

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
            return JsonResponse({"error": "Invalid user type"}, status=400)

        # Create User
        user_serializer = UserSerializer(data=body)
        if not user_serializer.is_valid():
            return JsonResponse(user_serializer.errors, status=400)

        user = user_serializer.save()

        # Prepare and create Profile
        profile_data = body.get("profile", {})
        profile_data["user"] = user.id

        profile_serializer = ProfileSerializer(data=profile_data)

        if profile_serializer.is_valid():
            profile_serializer.save()
            return JsonResponse(
                {"user": user_serializer.data, "profile": profile_serializer.data},
                status=201,
            )

        else:

            # Rollback user creation
            user.delete()
            return JsonResponse(profile_serializer.errors, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    except Exception as e:
        print("ERROR WHILE CREATING USER : ", e)
        return JsonResponse({"error": "Internal server error."}, status=500)


# @check_user_permission([{"subject": "user", "action": "read"}])
def get_user(request):
    all_users = User.objects.all()
    all_users_data = []

    profile_map = {
        "clubMember": (ClubMemberProfile, ClubMemberProfileSerializer),
        "studentCouncil": (StudentCouncilProfile, StudentCouncilProfileSerializer),
        "facultyAdvisor": (FacultyAdvisorProfile, FacultyAdvisorProfileSerializer),
        "studentWelfare": (StudentWelfareProfile, StudentWelfareProfileSerializer),
        "securityHead": (SecurityHeadProfile, SecurityHeadProfileSerializer),
    }

    for user in all_users:
        user_dict = {
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "role": {
                "id": user.role.id,
                "name": user.role.name,
                "description": user.role.description,
                "permissions": [
                    {"id": perm.id, "name": perm.name}
                    for perm in user.role.permissions.all()
                ],
            },
        }

        role_key = user.role.name  # e.g. “clubMember”
        prof_tup = profile_map.get(role_key)
        if prof_tup:
            model_cls, serializer_cls = prof_tup
            try:
                profile_inst = model_cls.objects.get(user=user)
                user_dict["profile"] = serializer_cls(profile_inst).data
            except model_cls.DoesNotExist:
                user_dict["profile"] = None

        all_users_data.append(user_dict)

    return JsonResponse(all_users_data, safe=False, status=200)


# @session_login_required
@check_user_permission([{"subject": "user", "action": "update"}])
def update_user(request):
    if request.method != "PUT":
        return JsonResponse({"error": "Only PUT method allowed."}, status=405)

    try:
        body = json.loads(request.body)
        user_type = request.GET.get("type")

        user_id = body.get("id")

        username = body.get("username")

        if not username:
            return JsonResponse({"error": "User ID is required."}, status=400)

        # ❌ Block if password is present
        if "password" in body:
            return JsonResponse(
                {"error": "Password cannot be updated from this endpoint."}, status=400
            )

        user = User.objects.get(username=username)

        # Update core User fields
        user_serializer = UserSerializer(user, data=body)
        if not user_serializer.is_valid():
            return JsonResponse(user_serializer.errors, status=400)
        user_serializer.save()

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
    except Exception:

        return JsonResponse({"error": "Internal server error."}, status=500)


# @check_user_permission([{"subject": "user", "action": "delete"}])
def delete_user(request):
    try:
        body = json.loads(request.body)
        print("DELETE REQUEST - Body received:", body)

        # Extract username from user object
        body = body.get("user", {})
        username = body.get("username")
        if not username:
            return JsonResponse({"error": "Username is required"}, status=400)

        print(f"Deleting user with username: {username}")
        user = User.objects.get(username=username)

        # Map user types to profile model attribute names
        profile_model_map = {
            "clubMember": "clubmemberprofile",
            "studentCouncil": "studentcouncilprofile",
            "facultyAdvisor": "facultyadvisorprofile",
            "studentWelfare": "studentwelfareprofile",
            "securityHead": "securityheadprofile",
        }

        # Delete profile based on user role
        role_name = user.role.name
        profile_attr = profile_model_map.get(role_name)

        if profile_attr:
            profile = getattr(user, profile_attr, None)
            if profile:
                print(f"Deleting {role_name} profile for user {username}")
                profile.delete()

        # Delete the user itself
        print(f"Deleting user {username}")
        user.delete()

        return JsonResponse(
            {"message": "User and profile deleted successfully"}, status=200
        )

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        print(f"Error during deletion: {str(e)}")
        return JsonResponse({"error": "Internal server error."}, status=500)


# @check_user_permission([{"subject": "user", "action": "write"}])
def map_user_to_role(request):
    body = json.loads(request.body)
    print(body)
    serializer = UserRoleSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


# @check_user_permission([{"subject": "user", "action": "write"}])
def unmap_user_role(request):
    # body = json.loads(request.body)
    # user_role = UserRole.objects.get(id=body["id"])
    # user_role.delete()
    return JsonResponse({"message": "User role deleted successfully"}, status=200)
