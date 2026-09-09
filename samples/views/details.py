from ..models import Sample
from ..forms import SampleForm

from lap_database.views import lap_form_handler


def sample_details(request, id=None):
    message = None
    if request.path.endswith("/new/"):
        message = (
            "Sample saved successfully.\nPlease verify that the Lot, SU, and Locale are correct before proceeding."
        )
    return lap_form_handler(request, Sample, SampleForm, id, message)
