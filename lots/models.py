from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from lapinfo.models import Season
from contexts.models import SU


class Lot(models.Model):
    CONTENTS_CHOICES = [
        ("foo", "foo"),
        ("bar", "bar"),
        ("baz", "baz"),
    ]
    number = models.CharField(
        max_length=9,
        default=Season.objects.last().name,  # type: ignore
        null=False,
    )  # type: ignore
    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        default=Season.objects.last().pk,
        null=False,
    )
    su = models.ForeignKey(
        SU,
        on_delete=models.PROTECT,
        null=False,
        verbose_name="SU",
    )
    dateassigned = models.DateField(
        null=False,
        default=timezone.now,
        verbose_name="Date Assigned",
    )
    contents = models.CharField(
        max_length=20,
        choices=CONTENTS_CHOICES,
        null=True,
        blank=True,
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
        db_table = "lap_lots"
        verbose_name_plural = "Lots"
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(
                Lower("number"),
                name="unique_lot_number",
                violation_error_message="This number already exists.",
            )
        ]

    def __str__(self):
        return self.number
