# from django.forms import ModelForm
from django import forms

from .models import Locale, Lot, SU


class LocaleForm(forms.ModelForm):
    class Meta:
        model = Locale
        fields = [
            "name",
            "area",
            "method",
            "notes",
        ]

    def __init__(self, *args, readonly=False, **kwargs):
        super(LocaleForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["formname"] = "locale"
        if readonly:
            for eachfield in self.Meta.fields:
                self.fields[eachfield].widget.attrs.update({"readonly": True})


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
            "color",
            "composition",
            "texture",
            "inclusions",
            "dimensions",
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

    def __init__(self, *args, readonly=False, **kwargs):
        super(SUForm, self).__init__(*args, **kwargs)
        self.fields["number"].widget.attrs["formname"] = "su"
        if readonly:
            for eachfield in self.Meta.fields:
                self.fields[eachfield].widget.attrs.update(
                    {"readonly": True, "onchange": "form.reset()"}
                )


class LotForm(forms.ModelForm):
    class Meta:
        model = Lot
        fields = [
            "number",
            "su",
            "contents",
            "season",
            "dateassigned",
            "notes",
            "voided",
        ]

    def __init__(self, *args, readonly=False, **kwargs):
        super(LotForm, self).__init__(*args, **kwargs)
        self.fields["number"].widget.attrs["formname"] = "lot"
        if readonly:
            for eachfield in self.Meta.fields:
                self.fields[eachfield].widget.attrs.update({"readonly": True})
