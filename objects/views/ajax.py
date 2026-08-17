from django.http import JsonResponse
from ..models import get_next_object_number, ObjectSubtype
from lots.models import Lot
from contexts.models import Locale


def load_objectsubtypes(request):
    objecttype_id = request.GET.get("objecttype_id")
    objectsubtypes = ObjectSubtype.objects.filter(type_id=objecttype_id)
    subtypes_list = []
    for each_subtype in objectsubtypes:
        subtypes_list.append((each_subtype.pk, each_subtype.name))
    return JsonResponse(subtypes_list, safe=False)


def load_nextnumber(request):
    season = request.GET.get("season")
    nextnumber = get_next_object_number(season)
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
