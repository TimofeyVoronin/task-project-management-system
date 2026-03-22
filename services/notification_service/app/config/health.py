from django.db import connections
from django.http import JsonResponse

SERVICE_NAME = "notification_service"


def healthcheck(request):
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse(
            {
                "status": "error",
                "service": SERVICE_NAME,
                "database": "unavailable",
            },
            status=503,
        )

    return JsonResponse(
        {
            "status": "ok",
            "service": SERVICE_NAME,
            "database": "ok",
        },
        status=200,
    )
