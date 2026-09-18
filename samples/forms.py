from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.db.models import F

from templates.widgets.widgets import CustomImageWidget
from lapinfo.models import Season
from contexts.models import Locale
from .models import Sample, SampleType


# List View Filters


class SampleFilters(forms.Form):
    locale = forms.ModelChoiceField(
        label="Locale",
        empty_label="all",
        queryset=Locale.objects.all()
        .extra(
            select={
                "sortorder": 'CASE WHEN "method" = "Survey" THEN "b-" || "name" WHEN "method" = "Surface Find" THEN "c-" || "name" WHEN substr("name", "LAPTT") THEN "a-" || "name" ELSE cast(substr("name", instr("name", " ") + 1, 3) as int) END'
            }
        )
        .order_by("sortorder"),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )
    type = forms.ModelChoiceField(
        label="Type",
        empty_label="all",
        queryset=SampleType.objects.all(),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )
    season = forms.ModelChoiceField(
        label="Season",
        empty_label="all",
        queryset=Season.objects.all(),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )


# Details View Forms


def _update_field_behavior(editable, ref):
    if editable:
        for eachfield in ref.fields:
            ref.fields[eachfield].widget.attrs.update({"oninput": "checkForm()"})
    else:
        for eachfield in ref.fields:
            ref.fields[eachfield].widget.attrs.update({"editable": True, "oninput": "form.reset()"})


class SampleForm(forms.ModelForm):
    su = forms.CharField(
        required=False,
        disabled=True,
        label="SU or 1LAP/3LAP Locus",
    )
    area = forms.CharField(
        required=False,
        disabled=True,
        label="Area",
    )
    locale = forms.CharField(
        required=False,
        disabled=True,
        label="Locale",
    )
    method = forms.CharField(
        required=False,
        disabled=True,
        label="Method",
    )

    class Meta:
        model = Sample
        fields = [
            "number",
            "excavationnumber",
            "season",
            "lot",
            "excavationdate",
            "registrationdate",
            "registrar",
            "sampletype",
            "box",
            "intendedanalysis",
            "notes",
            "voided",
        ]
        widgets = {
            "number": forms.TextInput(
                attrs={"pattern": r"^\d{1,2}LAP\.[sS]\.\d{3}$"},
            ),
            "excavationnumber": forms.TextInput(
                attrs={"pattern": r"^(\d{1,2}LAP\d{3}(/\d+)?(/[sS]?\d+)?)$"},
            ),
            "lot": AutocompleteSelect(
                Sample._meta.get_field("lot"),  # type: ignore
                admin.site,
            ),
            "excavationdate": forms.DateInput(
                attrs={"type": "date", "required": True},
                format="%Y-%m-%d",
            ),
            "registrationdate": forms.DateInput(
                attrs={"type": "date", "required": True},
                format="%Y-%m-%d",
            ),
        }

    def form_name(self):
        return "SampleForm"

    def __init__(self, *args, editable=False, **kwargs):
        user = kwargs.pop("user", None)
        super(SampleForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["su"].initial = self.instance.lot.su
            self.fields["area"].initial = self.instance.lot.su.locale.area
            self.fields["locale"].initial = self.instance.lot.su.locale
            self.fields["method"].initial = self.instance.lot.su.locale.method
        self.fields["registrar"].required = True
        self.fields["registrar"].initial = user
        self.fields["season"].widget.attrs["onChange"] = "loadNextRecordNumberForSeason('sample')"
        self.fields["voided"].widget.attrs["onchange"] = "voidedAlert();"
        _update_field_behavior(editable, self)
