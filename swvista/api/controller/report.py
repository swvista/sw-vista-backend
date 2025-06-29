from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import ReportSerializer


@api_view(["POST"])
def create_report(request):
    # Create a mutable copy of request data
    mutable_data = request.data.copy()
    # Add submitted_by from session
    mutable_data["submitted_by"] = request.session.get("user_id")

    serializer = ReportSerializer(data=mutable_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
