from django.http import JsonResponse
from ..models import Locale


def load_method(request):
    locale_id = request.GET.get("locale_id")
    locale = Locale.objects.filter(id=locale_id).last()
    response = {
        "method": str(locale.method),  # type: ignore
    }
    return JsonResponse(response, safe=False)
