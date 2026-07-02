from django.db import models
from django.db.models.functions import Lower
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
        null=False,
    )
    year = models.IntegerField(
        default=int(timezone.now().year),
        null=False,
        validators=[MinValueValidator(2019), MaxValueValidator(2030)],
    )  # type: ignore
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
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_season_name",
                violation_error_message="This name already exists.",
            )
        ]

    def __str__(self):
        return self.name

    def formatted_name(self):
        return f"{self.name} - {self.timeofyear} {self.year}"


class Area(models.Model):
    name = models.CharField(
        max_length=30,
        null=False,
    )
    shortname = models.CharField(
        max_length=5,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "lap_areas"
        verbose_name_plural = "Areas"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_area_name",
                violation_error_message="This name already exists.",
            ),
            models.UniqueConstraint(
                Lower("shortname"),
                name="unique_area_shortname",
                violation_error_message="This shortname already exists.",
            ),
        ]

    def __str__(self):
        return self.name

    def formatted_name(self):
        return self.name
