from django.http import JsonResponse
from ..models import Locale, SU


def load_locale(request):
    su_id = request.GET.get("su_id")
    locale_id = SU.objects.filter(id=su_id).values("locale_id")
    locale_name = Locale.objects.filter(id=locale_id[0]["locale_id"]).values("name")
    return JsonResponse(list(locale_name), safe=False)
