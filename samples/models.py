from django.db import models
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import CustomUser
from lapinfo.models import Season
from lots.models import Lot


def get_next_sample_number(selectedseason=None):
    currentseason = Season.objects.order_by("id").last().name  # type: ignore
    if selectedseason and selectedseason != currentseason:
        lastnumber = Sample.objects.filter(season__name=selectedseason).order_by("number").last().number  # type: ignore
        nextnumber = f"{selectedseason}.S.{int(lastnumber.split('LAP.S.')[1]) + 1:03d}"
    else:
        lastnumber = Sample.objects.all().order_by("number").last().number  # type: ignore
        if lastnumber.split("LAP.S.")[0] != currentseason.split("LAP.S.")[0]:
            nextnumber = f"{currentseason}.S.{int(currentseason.split('LAP.S.')[0]) + 1:03d}"
        else:
            nextnumber = f"{currentseason}.S.{int(lastnumber.split('LAP.S.')[1]) + 1:03d}"
    return nextnumber


class SampleType(models.Model):
    name = models.CharField(
        max_length=50,
        null=False,
        unique=True,
        verbose_name="Type",
    )

    class Meta:
        db_table = "lap_sampletypes"
        verbose_name_plural = "Sample Types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Sample(models.Model):
    number = models.CharField(
        max_length=13,
        default=get_next_sample_number,
        null=False,
    )
    excavationnumber = models.CharField(
        max_length=15,
        default=Season.objects.last().name,  # type: ignore
        null=False,
        verbose_name="Excavation Number",
    )
    lot = models.ForeignKey(
        Lot,
        on_delete=models.PROTECT,
        null=False,
    )
    excavationdate = models.DateField(
        null=True,
        blank=True,
        verbose_name="Excavation Date",
    )
    registrationdate = models.DateField(
        null=True,
        blank=True,
        default=timezone.now,
        verbose_name="Registration Date",
    )
    registrar = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        null=False,
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        default=Season.objects.last().pk,  # type: ignore
        null=False,
    )
    sampletype = models.ForeignKey(
        SampleType,
        on_delete=models.PROTECT,
        null=False,
    )
    box = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    intendedanalysis = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Intended Analysis",
    )
    notes = models.TextField(
        null=True,
        blank=True,
    )
    voided = models.BooleanField(
        null=False,
        default=False,
    )

    class Meta:
        db_table = "lap_samples"
        verbose_name_plural = "Samples"
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(
                Lower("number"),
                name="unique_sample_number",
                violation_error_message="This number already exists.",
            ),
        ]

    def __str__(self):
        return self.number

    def clean(self):
        if self.lot and f"{str(self.lot).split('LAP')[0]}LAP" != str(self.season):
            raise ValidationError("The lot given to this Object doesn’t match the Season.")

    def save(self, *args, **kwargs):
        self.number = self.number.upper()
        self.excavationnumber = self.excavationnumber.upper()
        super(Sample, self).save(*args, **kwargs)
