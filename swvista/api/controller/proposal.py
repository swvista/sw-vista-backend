import json

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from rbac.constants import roles
from rbac.models import User
from rbac.serializers import UserSerializer

from ..decorators import check_user_permission
from ..models.proposal import Proposal
from ..serializers import ProposalSerializer


@require_http_methods(["GET"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "proposal", "read")
def get_all_proposals(request):
    if request.session.get("user_id"):
        id = request.session.get("user_id")
        user = User.objects.get(id=id)
        user_data = UserSerializer(user)
        print(user_data)
    proposals = Proposal.objects.all()
    serializer = ProposalSerializer(proposals, many=True)
    return JsonResponse(serializer.data, safe=False)


# check for incoming request type ie post, get, put, delete using decorator


@require_http_methods(["GET"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "proposal", "read")
def get_proposal_by_id(request, id):
    print(request.method)
    proposal = Proposal.objects.get(id=id)

    serializer = ProposalSerializer(proposal)

    return JsonResponse(serializer.data, safe=False)


@require_http_methods(["POST"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "proposal", "write")
def create_proposal(request):
    data = json.loads(request.body)

    # check if the status is true made by it user, it should not allowed to be true when it is created it can be true when it is updated
    if "status" in data and data["status"]:
        return JsonResponse(
            {"message": "You are not allowed to create a proposal with status true"},
            status=400,
        )

    serializer = ProposalSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


@require_http_methods(["PUT"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "proposal", "write")
def update_proposal(request, id):
    proposal = Proposal.objects.get(id=id)
    if proposal.status == "approved" or proposal.status == "rejected":
        return JsonResponse(
            {
                "message": "You are not allowed to update a proposal with status approved or rejected"
            },
            status=400,
        )
    data = json.loads(request.body)
    serializer = ProposalSerializer(proposal, data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=200)
    return JsonResponse(serializer.errors, status=400)


@require_http_methods(["DELETE"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "proposal", "delete")
def delete_proposal(request, id):
    proposal = Proposal.objects.get(id=id)
    proposal.delete()
    return JsonResponse({"message": "Proposal deleted successfully"}, status=200)
