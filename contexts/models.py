from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.core.validators import MinValueValidator
from django.utils import timezone

from project.models import Area, Season


class Locale(models.Model):
    METHOD_CHOICES = [
        ("Excavation", "Excavation"),
        ("Scraping", "Scraping"),
        ("Survey", "Survey"),
        ("Surface Find", "Surface Find"),
    ]
    name = models.CharField(
        max_length=100,
        null=False,
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name="locales",
        null=False,
        default=Area.objects.filter(Q(name="Area H")).last(),
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        null=False,
        default="Scraping",
    )
    notes = models.TextField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "lap_locales"
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_locale_name",
                violation_error_message="This name already exists.",
            ),
        ]
        ordering = [
            F("name")[0:6],  # type: ignore
            "id",
        ]

    def __str__(self):
        return self.name

    def formatted_name(self):
        if self.name.startswith("Trench"):
            return f"{self.area.shortname}_{self.name}"  # type: ignore
        else:
            return self.name


class SUPrefix(models.Model):
    prefix = models.CharField(
        max_length=2,
        null=False,
    )
    feature = models.CharField(
        max_length=20,
        null=False,
    )

    class Meta:
        db_table = "lap_suprefixes"
        verbose_name_plural = "SU Prefixes"
        ordering = ["prefix"]
        constraints = [
            models.UniqueConstraint(
                Lower("prefix"),
                name="unique_prefix_prefix",
                violation_error_message="This prefix already exists.",
            ),
            models.UniqueConstraint(
                Lower("feature"),
                name="unique_prefix_feature",
                violation_error_message="This feature already exists.",
            ),
        ]

    def __str__(self):
        return self.feature

    def formatted_name(self):
        return f"{self.prefix} ({self.feature})"


class SU(models.Model):
    number = models.IntegerField(
        null=True,
        verbose_name="SU Number",
        validators=[MinValueValidator(0)],
    )
    locus = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="1/3LAP Locus",
    )
    locale = models.ForeignKey(
        Locale,
        on_delete=models.PROTECT,
        related_name="sus",
        null=False,
    )
    seasons = models.ManyToManyField(
        Season,
        verbose_name="Season(s)",
        default=Season.objects.last(),
    )
    dateassigned = models.DateField(
        null=False,
        default=timezone.now,
        verbose_name="Date Assigned",
    )
    recordedby = models.ForeignKey(
        "accounts.CustomUser",
        null=False,
        on_delete=models.PROTECT,
        verbose_name="Recorded By",
    )
    elevationtop = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Elevation (top)",
    )
    elevationbottom = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Elevation (bottom)",
    )
    color = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    composition = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    texture = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    inclusions = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    dimensions = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    sameas = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Same As",
    )
    coveredby = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Covered By",
    )
    covers = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    cutby = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Cut By",
    )
    abuts = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    cuts = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    filledby = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Filled By",
    )
    fills = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    prefix = models.ForeignKey(
        SUPrefix,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="SUs",
        verbose_name="Feature Type",
    )
    description = models.TextField(
        null=True,
        blank=True,
    )
    interpretation = models.TextField(
        null=True,
        blank=True,
    )
    architecturalfeatures = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Architectural Features",
    )
    architecturaltechnique = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Architectural Technique",
    )
    photogrammetrynumbers = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Photogrammetry Numbers",
    )
    photos = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    voided = models.BooleanField(
        null=False,
        default=False,
    )

    class Meta:
        db_table = "lap_sus"
        verbose_name_plural = "SUs"
        ordering = [
            F("number").asc(nulls_first=True),
            "locus",
            "locale",
        ]
        constraints = [
            models.UniqueConstraint(
                "number",
                name="unique_su_number",
                violation_error_message="This number already exists.",
            ),
            models.UniqueConstraint(
                Lower("locus"),
                name="unique_su_locus",
                violation_error_message="This locus already exists.",
            ),
        ]

    def __str__(self):
        if str(self.locus).startswith("Wall"):  # special case for a handful of contexts that were named "Wall n"
            return f"{self.locus}"
        elif self.locus:
            return f"Locus {self.locus}"
        elif self.prefix:
            return f"SU {self.prefix.prefix}.{self.number}"
        elif self.number is None:
            return f"SU 0 ({self.locale})"
        else:
            return f"SU {self.number}"
