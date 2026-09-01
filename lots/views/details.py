from ..models import Lot
from ..forms import LotForm

from lap_database.views import lap_form_handler


def lot_details(request, id=None):
    message = None
    if request.path.endswith("/new/"):
        message = "Lot saved successfully.\nPlease verify that the SU and Locale are correct before proceeding."
    return lap_form_handler(request, Lot, LotForm, id, message)
