from django.http import JsonResponse
from ..models import ObjectType, ObjectSubtype


def load_objectsubtypes(request):
    objecttype_id = request.GET.get("objecttype_id")
    objectsubtypes = ObjectSubtype.objects.filter(type_id=objecttype_id)
    subtypes_list = []
    for each_subtype in objectsubtypes:
        subtypes_list.append((each_subtype.pk, each_subtype.name))
    return JsonResponse(subtypes_list, safe=False)
