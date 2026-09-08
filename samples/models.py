from django.db import models


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
