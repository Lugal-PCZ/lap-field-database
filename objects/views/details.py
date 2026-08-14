from ..models import Object
from ..forms import ObjectForm

from lap_database.views import lap_form_handler


def object_details(request, id=None):
    return lap_form_handler(request, Object, ObjectForm, id)
