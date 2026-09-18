from django.http import JsonResponse
from contexts.models import SU


def load_locale(request):
    su_id = request.GET.get("su_id")
    su = SU.objects.filter(id=su_id).last()
    response = {
        "locale": str(su.locale),  # type: ignore
        "method": str(su.locale.method),  # type: ignore
        "area": str(su.locale.area),  # type: ignore
    }
    return JsonResponse(response, safe=False)
