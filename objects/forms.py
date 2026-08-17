from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.db.models import F

from lapinfo.models import Season
from contexts.models import Locale
from .models import Object, ObjectType, ObjectSubtype


# List View Filters


class SubtypeModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.formatted_name()


class ObjectFilters(forms.Form):
    season = forms.ModelChoiceField(
        label="Season",
        empty_label="all",
        queryset=Season.objects.all(),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )
    locale = forms.ModelChoiceField(
        label="Locale",
        empty_label="all",
        queryset=Locale.objects.all().order_by(F("name")[0:6], "id"),  # type: ignore
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )
    material = forms.ModelChoiceField(
        label="Material",
        empty_label="all",
        queryset=Object.objects.values_list("material", flat=True).order_by("material").distinct(),  # type: ignore
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )
    type = forms.ModelChoiceField(
        label="Type",
        empty_label="all",
        queryset=ObjectType.objects.all(),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )
    subtype = SubtypeModelChoiceField(
        label="Subtype",
        empty_label="all",
        queryset=ObjectSubtype.objects.all().order_by("name", "type"),
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


class ObjectForm(forms.ModelForm):
    su_display = forms.CharField(
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

    class Meta:
        model = Object
        fields = [
            "number",
            "excavationnumber",
            "season",
            "surfacefind",
            "lot",
            "su",
            "excavationdate",
            "registrationdate",
            "registrar",
            "objecttype",
            "objectsubtype",
            "sealingfunction",
            "clayslaborsealingmarking",
            "bladeserration",
            "preservation",
            "repairedorrepurposed",
            "material",
            "stonesubtype",
            "metalsubtype",
            "shellsubtype",
            "maincolor",
            "decoration",
            "decorationcolor",
            "height",
            "length",
            "width",
            "thickness",
            "diametermax",
            "diametermin",
            "diameterholes",
            "description",
            "notes",
            "senttobaghdad",
            "baghdadnumber",
            "tobephotographed",
            "photographed",
            "tobedrawn",
            "drawn",
            "voided",
        ]
        widgets = {
            "number": forms.TextInput(
                attrs={"pattern": r"^\d{1,2}LAP\d{5}$"},
            ),
            "excavationnumber": forms.TextInput(
                attrs={"pattern": r"^(\d{1,2}LAP\d{3}/[A-Za-z]{1,2})|([13]LAP\d{3}.\d{3})|([nN]/[aA])$"},
            ),
            "lot": AutocompleteSelect(
                Object._meta.get_field("lot"),  # type: ignore
                admin.site,
            ),
            "su": AutocompleteSelect(
                Object._meta.get_field("su"),  # type: ignore
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
        labels = {
            "excavationnumber": "Excavation Number (or N/A)",
        }

    def form_name(self):
        return "ObjectForm"

    def __init__(self, *args, editable=False, **kwargs):
        user = kwargs.pop("user", None)
        super(ObjectForm, self).__init__(*args, **kwargs)
        self.fields["su"].widget.attrs["initiallyhidden"] = True
        # self.fields["su_display"].widget.attrs["style"] = "grid-area: su;"
        if self.instance.pk:
            self.fields["su_display"].initial = self.instance.su
        self.fields["registrar"].initial = user
        self.fields["season"].widget.attrs["onChange"] = "loadNextObjectNumberForSeason()"
        if not self.instance:
            self.fields["lot"].required = True
        self.fields["objecttype"].widget.attrs["onChange"] = "loadObjectSubtypes()"
        subtypes = []
        if self.instance.pk:
            for each_subtype in ObjectSubtype.objects.filter(type_id=self.instance.objecttype):
                subtypes.append((each_subtype.pk, each_subtype.name))
        self.fields["objectsubtype"].choices = subtypes  # type: ignore
        if self.instance.objectsubtype:
            self.fields["objectsubtype"].initial = self.instance.objectsubtype.pk
        if not subtypes:
            self.fields["objectsubtype"].widget.attrs["initiallyhidden"] = True
        if not self.instance.material == "Stone":
            self.fields["stonesubtype"].widget.attrs["initiallyhidden"] = True
        if not self.instance.material == "Metal":
            self.fields["metalsubtype"].widget.attrs["initiallyhidden"] = True
        if not self.instance.material == "Shell":
            self.fields["shellsubtype"].widget.attrs["initiallyhidden"] = True
        if not self.instance.pk or not (
            self.instance.objecttype.name == "Administrative"
            and self.instance.objectsubtype.name in ["Clay Slab", "Sealing"]
        ):
            self.fields["clayslaborsealingmarking"].widget.attrs["initiallyhidden"] = True
        if not self.instance.pk or not (
            self.instance.objecttype.name == "Administrative" and self.instance.objectsubtype.name == "Sealing"
        ):
            self.fields["sealingfunction"].widget.attrs["initiallyhidden"] = True
        if not self.instance.pk or not self.instance.objectsubtype or self.instance.objectsubtype.name != "Blade":
            self.fields["bladeserration"].widget.attrs["initiallyhidden"] = True
        if not self.instance.senttobaghdad:
            self.fields["baghdadnumber"].widget.attrs["initiallyhidden"] = True
        _update_field_behavior(editable, self)
