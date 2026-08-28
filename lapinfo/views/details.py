from ..models import Area
from ..forms import AreaForm

from lap_database.views import lap_form_handler


def area_details(request, id=None):
    return lap_form_handler(request, Area, AreaForm, id)
