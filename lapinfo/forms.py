from django import forms

# from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
# from django.db.models import F, Q

# from lapinfo.models import Season
from contexts.models import Locale
from .models import Area


# Details View Form


def _update_field_behavior(editable, ref):
    if editable:
        for eachfield in ref.fields:
            ref.fields[eachfield].widget.attrs.update({"oninput": "checkForm()"})
    else:
        for eachfield in ref.fields:
            ref.fields[eachfield].widget.attrs.update({"editable": True, "oninput": "form.reset()"})


class AreaForm(forms.ModelForm):
    locales_list = forms.CharField(
        required=False,
        disabled=True,
        label="Locales",
        widget=forms.Textarea,
    )

    class Meta:
        model = Area
        fields = [
            "name",
            "shortname",
        ]

    def form_name(self):
        return "AreaForm"

    def __init__(self, *args, editable=False, **kwargs):
        user = kwargs.pop("user", None)
        super(AreaForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            locales_list = []
            for each_locale in self.instance.locales.values():
                locales_list.append(each_locale["name"])
            locales_list.sort()
            self.fields["locales_list"].initial = "; ".join(locales_list)
        _update_field_behavior(False, self)
