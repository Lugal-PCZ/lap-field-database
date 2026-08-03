from ..models import Lot
from ..forms import LotForm

from lap_database.views import lap_form_handler


def lot_details(request, id=None):
    return lap_form_handler(request, Lot, LotForm, id)
