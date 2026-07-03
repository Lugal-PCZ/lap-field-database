from ..models import Locale, SU
from ..forms import LocaleForm, SUForm

from lap_database.views import lap_form_handler


def locale_detail(request, id=None):
    return lap_form_handler(request, Locale, LocaleForm, id)


def su_detail(request, id=None):
    return lap_form_handler(request, SU, SUForm, id)
