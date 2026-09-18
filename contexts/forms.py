from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.db.models import F, Prefetch

from templates.widgets.widgets import CustomImageWidget, CustomWorldfileWidget
from lapinfo.models import Area, Season
from .models import Locale, SU, SUPrefix

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


# Details View Forms


def _update_field_behavior(editable, ref):
    if editable:
        for eachfield in ref.fields:
            ref.fields[eachfield].widget.attrs.update({"oninput": "checkForm()"})
    else:
        for eachfield in ref.fields:
            ref.fields[eachfield].widget.attrs.update({"editable": True, "oninput": "form.reset()"})


class LocaleForm(forms.ModelForm):
    seasons_list = forms.CharField(
        required=False,
        disabled=True,
        label="Seasons",
    )
    sus_list = forms.CharField(
        required=False,
        disabled=True,
        label="SUs and 1LAP/3LAP Loci",
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

    def form_name(self):
        return "LocaleForm"

    def __init__(self, *args, editable=False, **kwargs):
        user = kwargs.pop("user", None)
        super(LocaleForm, self).__init__(*args, **kwargs)
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
            self.fields["seasons_list"].initial = ", ".join(seasons)
            self.fields["sus_list"].initial = ", ".join(sus)
        _update_field_behavior(editable, self)


class SUForm(forms.ModelForm):
    method = forms.CharField(
        required=False,
        disabled=True,
        label="Method",
    )
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
            "worldfile",
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
            "notes",
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
            "worldfile": CustomWorldfileWidget(
                attrs={
                    "accept": ".jgw",
                }
            ),
        }

    def clean_number(self):
        if self.cleaned_data["number"] == 0:
            self.fields["number"].required = False
            self.cleaned_data["number"] = None
        return self.cleaned_data["number"]

    def form_name(self):
        return "SUForm"

    def __init__(self, *args, editable=False, **kwargs):
        user = kwargs.pop("user", None)
        super(SUForm, self).__init__(*args, **kwargs)
        if not self.instance.number:
            self.fields["number"].widget.attrs["value"] = 0
        self.fields["recordedby"].initial = user
        self.fields["locus"].disabled = True
        self.fields["seasons"].widget.attrs["size"] = Season.objects.all().count()
        self.fields["tracing"].widget.attrs["onscreen"] = f"/{str(self.instance.tracing_onscreen)}"
        self.fields["tracing"].widget.attrs["user"] = str(user)
        self.fields["worldfile"].widget.attrs["user"] = str(user)
        if not self.instance.worldfile_contents:
            self.fields["worldfile"].widget.attrs["initiallyhidden"] = True
        if self.instance.worldfile_contents:
            self.fields["worldfile"].widget.attrs["value"] = f"{self.instance.worldfile_contents}"
        if self.instance.pk:
            self.fields["method"].initial = self.instance.locale.method
            related_lots = self.instance.lot_set.values()
            lots = set()
            for each_lot in related_lots:
                lots.add(each_lot["number"])
            lots = list(lots)
            lots.sort()
            self.fields["lots_list"].initial = ", ".join(lots)
        self.fields["locale"].widget.attrs["onchange"] = "loadMethod('su');"
        self.fields["voided"].widget.attrs["onchange"] = "voidedAlert();"
        _update_field_behavior(editable, self)
