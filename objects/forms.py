from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.db.models import F

from lapinfo.models import Season
from contexts.models import Locale
from .models import Object, ObjectType, ObjectSubtype


# List View Filters


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
    type = forms.ModelChoiceField(
        label="Type",
        empty_label="all",
        queryset=ObjectType.objects.all(),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )
    subtype = forms.ModelChoiceField(
        label="Subtype",
        empty_label="all",
        queryset=ObjectSubtype.objects.all(),
        widget=forms.Select(attrs={"onchange": "submitCleanURL(this.form)"}),
    )


# Details View Forms


# def _update_field_behavior(editable, ref):
#     if editable:
#         for eachfield in ref.Meta.fields:
#             ref.fields[eachfield].widget.attrs.update({"oninput": "checkForm()"})
#     else:
#         for eachfield in ref.Meta.fields:
#             ref.fields[eachfield].widget.attrs.update({"editable": True, "oninput": "form.reset()"})


# class ObjectForm(forms.ModelForm):
#     locale = forms.CharField(
#         required=False,
#         disabled=True,
#     )

#     class Meta:
#         model = Object
#         fields = [
#             "number",
#             "su",
#             "contents",
#             "dateassigned",
#             "season",
#             "notes",
#             "voided",
#         ]
#         widgets = {
#             "number": forms.TextInput(
#                 attrs={"pattern": r"^\d{1,2}LAP\d{3}$"},
#             ),
#             "dateassigned": forms.DateInput(
#                 attrs={"type": "date"},
#                 format="%Y-%m-%d",
#             ),
#             "su": AutocompleteSelect(
#                 Lot._meta.get_field("su"),  # type: ignore
#                 admin.site,
#             ),
#         }

#     def form_name(self):
#         return "LotForm"

#     def __init__(self, *args, editable=False, **kwargs):
#         user = kwargs.pop("user", None)
#         super(LotForm, self).__init__(*args, **kwargs)
#         self.fields["su"].widget.attrs["onChange"] = "loadLocale()"
#         if self.instance and hasattr(self.instance, "su"):
#             self.fields["locale"].initial = self.instance.su.locale
#         _update_field_behavior(editable, self)
