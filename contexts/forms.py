from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.db.models import Q

from .models import Area, Locale, Lot, Season, SU, SUPrefix


# List View Filters


class LocaleFilters(forms.Form):
    area = forms.ModelChoiceField(
        label="Area",
        empty_label="all",
        queryset=Area.objects.all(),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )


class SUFilters(forms.Form):
    locale = forms.ModelChoiceField(
        label="Locale",
        empty_label="all",
        queryset=Locale.objects.all(),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )
    type = forms.ModelChoiceField(
        label="Feature Type",
        empty_label="all",
        queryset=SUPrefix.objects.all(),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )
    season = forms.ModelChoiceField(
        label="Season",
        empty_label="all",
        queryset=Season.objects.all(),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )


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
        queryset=Locale.objects.all(),
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


# Detail View Forms


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
        user = kwargs.pop("user", None)
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

    def clean_number(self):
        if self.cleaned_data["number"] == 0:
            self.fields["number"].required = False
            self.cleaned_data["number"] = None
        return self.cleaned_data["number"]

    def __init__(self, *args, editable=False, **kwargs):
        user = kwargs.pop("user", None)
        super(SUForm, self).__init__(*args, **kwargs)
        self.fields["number"].widget.attrs["formname"] = "su"
        if not self.instance.number:
            self.fields["number"].widget.attrs["value"] = 0
        self.fields["recordedby"].initial = user
        _update_field_behavior(editable, self)


class LotForm(forms.ModelForm):
    locale = forms.CharField(required=False, disabled=True)

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
        user = kwargs.pop("user", None)
        super(LotForm, self).__init__(*args, **kwargs)
        self.fields["number"].widget.attrs["formname"] = "lot"
        self.fields["su"].widget.attrs["onChange"] = f"loadLocale()"
        if self.instance and hasattr(self.instance, "su"):
            self.fields["locale"].initial = self.instance.su.locale
        _update_field_behavior(editable, self)
