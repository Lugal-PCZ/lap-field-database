from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.db.models import F, Prefetch, Q

from templates.widgets.widgets import CustomImageWidget
from lapinfo.models import Area, Season
from .models import Locale, SU, SUPrefix
from lots.models import Lot

# List View Filters


class LocaleFilters(forms.Form):
    area = forms.ModelChoiceField(
        label="Area",
        empty_label="all",
        queryset=Area.objects.all(),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )
    season = forms.ModelChoiceField(
        label="Season",
        empty_label="all",
        queryset=Season.objects.all(),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )


class SUFilters(forms.Form):
    locale = forms.ModelChoiceField(
        label="Locale",
        empty_label="all",
        queryset=Locale.objects.all().order_by(F("name")[0:6], "id"),  # type: ignore
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
        queryset=Locale.objects.all().order_by(F("name")[0:6], "id"),  # type: ignore
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
    seasons_list = forms.CharField(
        required=False,
        disabled=True,
        label="Season(s)",
    )
    sus_list = forms.CharField(
        required=False,
        disabled=True,
        label="SUs",
        widget=forms.Textarea,
    )

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
        if self.instance.pk:
            related_sus = self.instance.sus.prefetch_related(
                Prefetch(
                    "seasons",
                    queryset=Season.objects.all(),
                    to_attr="seasons_list",
                )
            )
            seasons = set()
            sus = []
            for each_su in related_sus:
                for each_season in each_su.seasons_list:
                    seasons.add(str(each_season))
                sus.append(str(each_su))
            seasons = list(seasons)
            seasons.sort()
            self.fields["seasons_list"].widget.attrs["value"] = ", ".join(seasons)
            self.fields["sus_list"].initial = ", ".join(sus)
        _update_field_behavior(editable, self)


class SUForm(forms.ModelForm):
    lots_list = forms.CharField(
        required=False,
        disabled=True,
        label="Lots",
    )

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
            "tracing",
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
            "dateassigned": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "locale": AutocompleteSelect(
                SU._meta.get_field("locale"),  # type: ignore
                admin.site,
            ),
            "tracing": CustomImageWidget(
                attrs={
                    "accept": ".jpg,.jpeg",
                },
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
        self.fields["locus"].disabled = True
        self.fields["tracing"].widget.attrs["onscreen"] = f"/{str(self.instance.tracing_onscreen)}"
        self.fields["tracing"].widget.attrs["user"] = str(user)
        if self.instance.pk:
            related_lots = self.instance.lot_set.values()
            lots = set()
            for each_lot in related_lots:
                lots.add(each_lot["number"])
            lots = list(lots)
            lots.sort()
            self.fields["lots_list"].widget.attrs["value"] = ", ".join(lots)
        _update_field_behavior(editable, self)
