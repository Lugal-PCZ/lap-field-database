from datetime import date
from django.db import models
from django.db.models import Q
from django.core.validators import MaxValueValidator, MinValueValidator


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
        default=date.today().year,
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
        ordering = ["-id"]

    def __str__(self):
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
    )

    class Meta:
        db_table = "lap_areas"
        verbose_name_plural = "Areas"
        ordering = ["name"]

    def __str__(self):
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
        return f"{self.prefix} - {self.feature}"


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
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        null=False,
        default="Excavation",
    )
    seasons = models.ManyToManyField(
        Season,
        verbose_name="Season(s)",
        default=Season.objects.all()[0].pk,
    )

    class Meta:
        db_table = "lap_locales"
        unique_together = ["name", "area"]
        ordering = ["name"]

    def __str__(self):
        locale_seasons = [season["name"] for season in self.seasons.values()]
        if self.name.upper().startswith("TRENCH") and self.area.name.upper().startswith(
            "AREA"
        ):
            return f"{self.area.name.split(' ')[1]}_{self.name} ({', '.join(locale_seasons)})"
        elif self.method == "Excavation":  # Test Trenches/Soundings
            return f"{self.name} ({', '.join(locale_seasons)})"
        else:
            return f"{self.area}: {self.name} ({', '.join(locale_seasons)})"


class SU(models.Model):
    number = models.IntegerField(unique=True, null=True)
    locuslayer = models.CharField(
        max_length=5,
        unique=True,
        null=True,
        verbose_name="1LAP/3LAP Locus.Layer",
    )
    locale = models.ForeignKey(
        Locale,
        on_delete=models.PROTECT,
        related_name="sus",
        null=False,
        limit_choices_to=Q(method="Excavation")
        | Q(method="Scraping")
        | Q(method="Survey"),
    )
    seasons = models.ManyToManyField(
        Season,
        verbose_name="Season(s)",
        default=Season.objects.all()[0].pk,
    )
    dateassigned = models.DateField(
        null=False,
        auto_now=True,
        verbose_name="Date Assigned",
    )
    author = models.ForeignKey(
        "accounts.CustomUser",
        null=False,
        on_delete=models.PROTECT,
    )
    elevationtop = models.CharField(
        max_length=50,
        null=True,
        verbose_name="Elevation (top)",
    )
    elevationbottom = models.CharField(
        max_length=50,
        null=True,
        verbose_name="Elevation (bottom)",
    )
    color = models.CharField(
        max_length=50,
        null=True,
    )
    composition = models.CharField(
        max_length=50,
        null=True,
    )
    texture = models.CharField(
        max_length=50,
        null=True,
    )
    inclusions = models.CharField(
        max_length=50,
        null=True,
    )
    dimensions = models.CharField(
        max_length=50,
        null=True,
    )
    sameas = models.CharField(
        max_length=50,
        null=True,
        verbose_name="Same As",
    )
    coveredby = models.CharField(
        max_length=50,
        null=True,
        verbose_name="Covered By",
    )
    covers = models.CharField(
        max_length=50,
        null=True,
    )
    cutby = models.CharField(
        max_length=50,
        null=True,
        verbose_name="Cut By",
    )
    abuts = models.CharField(
        max_length=50,
        null=True,
    )
    cuts = models.CharField(
        max_length=50,
        null=True,
    )
    filledby = models.CharField(
        max_length=50,
        null=True,
        verbose_name="Filled By",
    )
    fills = models.CharField(
        max_length=50,
        null=True,
    )
    prefix = models.ForeignKey(
        SUPrefix,
        on_delete=models.PROTECT,
        null=True,
        related_name="SUs",
    )
    description = models.TextField(
        null=True,
    )
    interpretation = models.TextField(
        null=True,
    )
    architecturalfeatures = models.CharField(
        max_length=100,
        null=True,
        verbose_name="Architectural Features",
    )
    architecturaltechnique = models.CharField(
        max_length=100,
        null=True,
        verbose_name="Architectural Technique",
    )
    photogrammetrynumbers = models.CharField(
        max_length=200,
        null=True,
        verbose_name="Photogrammetry Numbers",
    )
    photos = models.CharField(
        max_length=200,
        null=True,
    )

    class Meta:
        db_table = "lap_sus"
        verbose_name_plural = "SUs"
        ordering = ["number"]

    def __str__(self):
        return f"SU{self.number} - {self.locale}"


class Lot(models.Model):
    number = models.CharField(
        max_length=8,
        default=Season.objects.all()[0].name,
        unique=True,
        null=False,
    )
    su = models.ForeignKey(
        SU,
        on_delete=models.PROTECT,
        null=False,
    )

    class Meta:
        db_table = "lap_lots"
        verbose_name_plural = "Lots"
        ordering = ["number"]

    def __str__(self):
        return self.number
