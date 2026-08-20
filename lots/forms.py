from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.db.models import F, Q

from lapinfo.models import Season
from contexts.models import Locale, SU
from .models import Lot


# List View Filters


class LotFilters(forms.Form):
    su = forms.ModelChoiceField(
        label="SU",
        empty_label="all",
        queryset=SU.objects.filter(Q(number__isnull=False) | Q(locus__isnull=False)),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )
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
    contents = forms.ModelChoiceField(
        label="Contents",
        empty_label="all",
        queryset=Lot.objects.values_list("contents", flat=True).order_by("contents").distinct(),  # type: ignore
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


class LotForm(forms.ModelForm):
    locale = forms.CharField(
        required=False,
        disabled=True,
    )
    contents = forms.CharField(
        required=False,
        disabled=True,
        initial="(general/pottery)",
    )

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
            "number": forms.TextInput(
                attrs={"pattern": r"^\d{1,2}LAP\d{3,4}$"},
            ),
            "dateassigned": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "su": AutocompleteSelect(
                Lot._meta.get_field("su"),  # type: ignore
                admin.site,
            ),
        }
        labels = {
            "su": "SU or 1LAP/3LAP Locus",
        }

    def form_name(self):
        return "LotForm"

    def __init__(self, *args, editable=False, **kwargs):
        user = kwargs.pop("user", None)
        super(LotForm, self).__init__(*args, **kwargs)
        self.fields["su"].widget.attrs["onChange"] = "loadLocale()"
        if self.instance and hasattr(self.instance, "su"):
            self.fields["locale"].initial = self.instance.su.locale
        self.fields["voided"].widget.attrs["onchange"] = "voidedAlert();"
        _update_field_behavior(editable, self)
