from ..models import Object
from ..forms import ObjectForm

from lap_database.views import lap_form_handler


def object_details(request, id=None):
    message = "Object saved successfully.\nPlease verify that the Lot, SU, and Locale are correct before proceeding."
    return lap_form_handler(request, Object, ObjectForm, id, message)
