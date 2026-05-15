from django import forms
from django.db.models import Q

from .models import Area, Locale, Lot, Season, SU, SUPrefix


class LocaleFilters(forms.Form):
    area = forms.ModelChoiceField(
        label="Area",
        empty_label="all",
        queryset=Area.objects.all(),
        widget=forms.Select(attrs={"onchange": "this.form.submit()"}),
    )


class SUFilters(forms.Form):
    locale = forms.ModelChoiceField(
        label="Locale",
        empty_label="all",
        queryset=Locale.objects.all(),
        widget=forms.Select(attrs={"onchange": "this.form.submit()"}),
    )
    type = forms.ModelChoiceField(
        label="Feature Type",
        empty_label="all",
        queryset=SUPrefix.objects.all(),
        widget=forms.Select(attrs={"onchange": "this.form.submit()"}),
    )
    season = forms.ModelChoiceField(
        label="Season",
        empty_label="all",
        queryset=Season.objects.all(),
        widget=forms.Select(attrs={"onchange": "this.form.submit()"}),
    )


class LotFilters(forms.Form):
    su = forms.ModelChoiceField(
        label="SU",
        empty_label="all",
        queryset=SU.objects.filter(Q(number__isnull=False) | Q(locus__isnull=False)),
        widget=forms.Select(attrs={"onchange": "this.form.submit()"}),
    )
    locale = forms.ModelChoiceField(
        label="Locale",
        empty_label="all",
        queryset=Locale.objects.all(),
        widget=forms.Select(attrs={"onchange": "this.form.submit()"}),
    )
    contents = forms.ModelChoiceField(
        label="Contents",
        empty_label="all",
        queryset=Lot.objects.values_list("contents", flat=True)
        .order_by("contents")
        .distinct(),  # type: ignore
        widget=forms.Select(attrs={"onchange": "this.form.submit()"}),
    )
    season = forms.ModelChoiceField(
        label="Season",
        empty_label="all",
        queryset=Season.objects.all(),
        widget=forms.Select(attrs={"onchange": "this.form.submit()"}),
    )
