from django.http import JsonResponse


def index(request):
    # api health checker  -> NOTE no auth required
    return JsonResponse({"message": "HEALTH CHECK!!!"})
