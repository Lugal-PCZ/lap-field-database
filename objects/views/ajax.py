from django.http import JsonResponse
from ..models import get_next_object_number, ObjectSubtype


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
