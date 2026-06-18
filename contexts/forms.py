# from django.forms import ModelForm
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect

from .models import Locale, Lot, SU


def _update_field_behavior(editable, ref):
    if editable:
        for eachfield in ref.Meta.fields:
            ref.fields[eachfield].widget.attrs.update({"oninput": "checkForm()"})
    else:
        for eachfield in ref.Meta.fields:
            ref.fields[eachfield].widget.attrs.update({"editable": True, "oninput": "form.reset()"})


class LocaleForm(forms.ModelForm):
    class Meta:
        model = Locale
        fields = [
            "name",
            "area",
            "method",
            "notes",
        ]

    def __init__(self, *args, editable=False, **kwargs):
        super(LocaleForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["formname"] = "locale"
        _update_field_behavior(editable, self)


class SUForm(forms.ModelForm):
    class Meta:
        model = SU
        fields = [
            "number",
            "locus",
            "locale",
            "dateassigned",
            "recordedby",
            "seasons",
            "prefix",
            "architecturalfeatures",
            "architecturaltechnique",
            "elevationtop",
            "elevationbottom",
            "dimensions",
            "color",
            "composition",
            "texture",
            "inclusions",
            "sameas",
            "abuts",
            "coveredby",
            "covers",
            "cutby",
            "cuts",
            "filledby",
            "fills",
            "description",
            "interpretation",
            "photos",
            "photogrammetrynumbers",
            "voided",
        ]
        widgets = {
            "dateassigned": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "locale": AutocompleteSelect(
                SU._meta.get_field("locale"),  # type: ignore
                admin.site,
            ),
        }

    def __init__(self, *args, editable=False, **kwargs):
        self.user = kwargs.pop("user", None)
        super(SUForm, self).__init__(*args, **kwargs)
        self.fields["number"].widget.attrs["formname"] = "su"
        self.fields["recordedby"].initial = self.user.id
        _update_field_behavior(editable, self)


class LotForm(forms.ModelForm):
    class Meta:
        model = Lot
        fields = [
            "number",
            "su",
            "contents",
            "dateassigned",
            "season",
            "notes",
            "voided",
        ]
        widgets = {
            "dateassigned": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "su": AutocompleteSelect(
                Lot._meta.get_field("su"),  # type: ignore
                admin.site,
            ),
        }

    def __init__(self, *args, editable=False, **kwargs):
        super(LotForm, self).__init__(*args, **kwargs)
        self.fields["number"].widget.attrs["formname"] = "lot"
        _update_field_behavior(editable, self)
