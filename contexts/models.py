from django.db import models
from django.db.models import F
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone


class Season(models.Model):
    TIME_OF_YEAR_CHOICES = [
        ("Winter", "Winter"),
        ("Spring", "Spring"),
        ("Summer", "Summer"),
        ("Fall", "Fall"),
    ]
    name = models.CharField(
        max_length=5,
        unique=True,
        null=False,
    )
    year = models.IntegerField(
        validators=[MinValueValidator(2019), MaxValueValidator(2030)],
        default=timezone.now().year,
        null=False,
    )
    timeofyear = models.CharField(
        max_length=6,
        choices=TIME_OF_YEAR_CHOICES,
        null=False,
        verbose_name="Time of Year",
    )

    class Meta:
        db_table = "lap_seasons"
        verbose_name_plural = "Seasons"
        ordering = ["id"]

    def __str__(self):
        return self.name

    def formatted_name(self):
        return f"{self.name} - {self.timeofyear} {self.year}"


class Area(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True,
        null=False,
    )
    shortname = models.CharField(
        max_length=5,
        unique=True,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "lap_areas"
        verbose_name_plural = "Areas"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def formatted_name(self):
        return self.name


class Locale(models.Model):
    METHOD_CHOICES = [
        ("Excavation", "Excavation"),
        ("Scraping", "Scraping"),
        ("Survey", "Survey"),
        ("Surface Find", "Surface Find"),
    ]
    name = models.CharField(
        max_length=100,
        unique=True,
        null=False,
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name="locales",
        null=False,
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        null=False,
        default="Excavation",
    )
    notes = models.TextField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "lap_locales"
        ordering = [F("name")[0:7]]  # type: ignore

    def __str__(self):
        return self.name

    def formatted_name(self):
        if self.name.startswith("Trench"):
            return f"{self.area.shortname}_{self.name}"
        else:
            return self.name


class SUPrefix(models.Model):
    prefix = models.CharField(
        max_length=2,
        unique=True,
        null=False,
    )
    feature = models.CharField(
        max_length=20,
        unique=True,
        null=False,
    )

    class Meta:
        db_table = "lap_suprefixes"
        verbose_name_plural = "SU Prefixes"
        ordering = ["prefix"]

    def __str__(self):
        return self.feature

    def formatted_name(self):
        return f"{self.prefix} ({self.feature})"


class SU(models.Model):
    number = models.IntegerField(
        unique=True,
        null=True,
        verbose_name="SU",
    )
    locus = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        verbose_name="1LAP/3LAP Locus",
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
        default=timezone.now().date,
        verbose_name="Date Assigned",
    )
    recordedby = models.ForeignKey(
        "accounts.CustomUser",
        null=False,
        on_delete=models.PROTECT,
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
            F("number").asc(nulls_last=True),
            "locus",
            "locale",
        ]

    def __str__(self):
        if str(self.locus).startswith("Wall"):  # special case for a handful of contexts that were named "Wall n"
            return f"{self.locus}"
        elif self.locus:
            return f"Locus {self.locus}"
        elif self.prefix:
            return f"SU {self.prefix.prefix}.{self.number}"
        elif self.number is None:
            return "SU 0"
        else:
            return f"SU {self.number}"


class Lot(models.Model):
    CONTENTS_CHOICES = [
        ("foo", "foo"),
        ("bar", "bar"),
        ("baz", "baz"),
    ]
    number = models.CharField(
        max_length=8,
        default=Season.objects.reverse()[0].name,
        unique=True,
        null=False,
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        default=Season.objects.last(),
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
        default=timezone.now().date,
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

    def __str__(self):
        return self.number
