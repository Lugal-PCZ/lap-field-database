from ..models import Locale, SU
from ..forms import LocaleForm, SUForm

from lap_database.views import lap_form_handler


def locale_details(request, id=None):
    return lap_form_handler(request, Locale, LocaleForm, id)


def su_details(request, id=None):
    message = "SU saved successfully.\nPlease verify that the Locale is correct before proceeding."
    return lap_form_handler(request, SU, SUForm, id, message)
