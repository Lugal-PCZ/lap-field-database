from django.http import JsonResponse
from ..models import get_next_sample_number
from contexts.models import SU
from lots.models import Lot


def load_nextnumber(request):
    season = request.GET.get("season")
    nextnumber = get_next_sample_number(season)
    return JsonResponse(nextnumber, safe=False)


def load_su(request):
    lot_id = request.GET.get("lot_id")
    lot = Lot.objects.filter(id=lot_id).last()
    su = lot.su  # type: ignore
    locale = lot.su.locale  # type: ignore
    response = {
        "su": {"id": su.id, "name": str(su)},  # type: ignore
        "locale": str(locale),
        "area": str(locale.area),
        "lot_dateassigned": lot.dateassigned,  # type: ignore
    }
    return JsonResponse(response, safe=False)


def load_locale(request):
    su_id = request.GET.get("su_id")
    su = SU.objects.filter(id=su_id).last()
    response = {
        "locale": str(su.locale),  # type: ignore
        "area": str(su.locale.area),  # type: ignore
    }
    return JsonResponse(response, safe=False)
