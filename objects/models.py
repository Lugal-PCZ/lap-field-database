from django.db import models
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import CustomUser
from lapinfo.models import Area, Season
from contexts.models import Locale, SU
from lots.models import Lot


class ObjectType(models.Model):
    name = models.CharField(
        max_length=50,
        null=False,
        unique=True,
        verbose_name="Type",
    )

    class Meta:
        db_table = "lap_objecttypes"
        verbose_name_plural = "Object Types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ObjectSubtype(models.Model):
    name = models.CharField(
        max_length=50,
        null=False,
        verbose_name="Subtype",
    )
    type = models.ForeignKey(
        ObjectType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "lap_objectsubtypes"
        unique_together = ["type", "name"]
        verbose_name_plural = "Object Subtypes"
        ordering = ["type", "name"]

    def __str__(self):
        return f"{self.type}: {self.name}"


class Object(models.Model):
    SEALINGFUNCTION_CHOICES = [
        ("Bag", "Bag"),
        ("Basket", "Basket"),
        ("Box", "Box"),
        ("Door", "Door"),
        ("Jar", "Jar"),
        ("Package", "Package"),
        ("Squeeze", "Squeeze"),
        ("Stopper", "Stopper"),
        ("Uncertain", "Uncertain"),
    ]
    CLAYSLABORSEALINGMARKING_CHOICES = [
        ("Marked", "Marked"),
        ("Seal Impressed", "Seal Impressed"),
        ("Unmarked", "Unmarked"),
    ]
    BLADESERRATION_CHOICES = [
        ("Smooth", "Smooth"),
        ("One Edge", "One Edge"),
        ("Both Edges", "Both Edges"),
    ]
    PRESERVATION_CHOICES = [
        ("Fragmentary", "Fragmentary"),
        ("Nearly Complete", "Nearly Complete"),
        ("Complete", "Complete"),
        ("Rim", "Rim"),
        ("Base", "Base"),
        ("Full Profile", "Full Profile"),
    ]
    REPAIREDORREPURPOSED_CHOICES = [
        ("None Evident", "None Evident"),
        ("Repaired", "Repaired"),
        ("Repurposed", "Repurposed"),
        ("Repurposed and Repaired", "Repurposed and Repaired"),
        ("(not recorded)", "(not recorded)"),
    ]
    MATERIAL_CHOICES = [
        ("Bitumen", "Bitumen"),
        ("Bone", "Bone"),
        ("Brick", "Brick"),
        ("Clay, Baked", "Clay, Baked"),
        ("Clay, Unbaked", "Clay, Unbaked"),
        ("Glass", "Glass"),
        ("Metal", "Metal"),
        ("Shell", "Shell"),
        ("Slag", "Slag"),
        ("Stone", "Stone"),
        ("Tooth", "Tooth"),
    ]
    STONESUBTYPE_CHOICES = [
        ("Basalt", "Basalt"),
        ("Basalt?", "Basalt?"),
        ("“Beach Stone”", "“Beach Stone”"),
        ("Calcite", "Calcite"),
        ("Calcite?", "Calcite?"),
        ("Carnelian", "Carnelian"),
        ("Carnelian?", "Carnelian?"),
        ("Chalcedony", "Chalcedony"),
        ("Chalcedony?", "Chalcedony?"),
        ("Chert", "Chert"),
        ("Chert?", "Chert?"),
        ("Chlorite/Steatite", "Chlorite/Steatite"),
        ("Chlorite/Steatite?", "Chlorite/Steatite?"),
        ("Diorite", "Diorite"),
        ("Diorite?", "Diorite?"),
        ("Granite", "Granite"),
        ("Granite?", "Granite?"),
        ("Hematite", "Hematite"),
        ("Hematite?", "Hematite?"),
        ("Lapis", "Lapis"),
        ("Lapis?", "Lapis?"),
        ("Limestone", "Limestone"),
        ("Limestone?", "Limestone?"),
        ("Quartz", "Quartz"),
        ("Quartz?", "Quartz?"),
        ("Rock Crystal", "Rock Crystal"),
        ("Rock Crystal?", "Rock Crystal?"),
        ("Sandstone", "Sandstone"),
        ("Sandstone?", "Sandstone?"),
        ("Schist", "Schist"),
        ("Schist?", "Schist?"),
        ("Sedimentary, Other", "Sedimentary, Other"),
        ("Serpentine", "Serpentine"),
        ("Serpentine?", "Serpentine?"),
        ("Soapstone", "Soapstone"),
        ("Soapstone?", "Soapstone?"),
        ("Unidentified", "Unidentified"),
    ]
    METALSUBTYPE_CHOICES = [
        ("Copper/Bronze", "Copper/Bronze"),
        ("Gold", "Gold"),
        ("Iron", "Iron"),
        ("Lead", "Lead"),
        ("Silver", "Silver"),
    ]
    COLOR_CHOICES = [
        ("Beige", "Beige"),
        ("Black", "Black"),
        ("Blue", "Blue"),
        ("Brown", "Brown"),
        ("Colorless", "Colorless"),
        ("Green", "Green"),
        ("Grey", "Grey"),
        ("Orange", "Orange"),
        ("Pink", "Pink"),
        ("Purple", "Purple"),
        ("Red", "Red"),
        ("Turquoise", "Turquoise"),
        ("White", "White"),
        ("Yellow", "Yellow"),
        ("(not recorded)", "(not recorded)"),
    ]
    DECORATION_CHOICES = [
        ("Carved", "Carved"),
        ("Glazed", "Glazed"),
        ("Impressed", "Impressed"),
        ("Incised", "Incised"),
        ("Painted", "Painted"),
        ("Polished", "Polished"),
    ]
    number = models.CharField(
        max_length=10,
        default=Season.objects.last().name,  # type: ignore
        null=False,
    )
    excavationnumber = models.CharField(
        max_length=12,
        default=Season.objects.last().name,  # type: ignore
        null=False,
        verbose_name="Excavation Number",
        # TODO: make sure that "N/A" can be entered for incidental surface finds
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        default=Season.objects.last().pk,  # type: ignore
        null=False,
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        null=False,
        # TODO: in the form, this should filter the possible locales
    )
    locale = models.ForeignKey(
        Locale,
        on_delete=models.PROTECT,
        null=False,
        # TODO: in the form, this and Season together should filter the possible SUs
    )
    su = models.ForeignKey(
        SU,
        on_delete=models.PROTECT,
        null=False,
        verbose_name="SU or 1LAP/3LAP Locus",
    )
    lot = models.ForeignKey(
        Lot,
        on_delete=models.PROTECT,
        default=Season.objects.last().name,  # type: ignore
        null=True,
        blank=True,
        # TODO: if Lot is given, its date must match the excavation date
    )
    excavationdate = models.DateField(
        null=True,
        blank=True,
        default=timezone.now,
        verbose_name="Excavation Date",
        # TODO: best would be if this auto-populated with the Lot's date
        # TODO: there are many NULLs in the legacy data, so this has to be nullable, but enforce required in the form
    )
    registrationdate = models.DateField(
        null=True,
        blank=True,
        default=timezone.now,
        verbose_name="Registration Date",
        # TODO: there are many NULLs in the legacy data, so this has to be nullable, but enforce required in the form
    )
    registrar = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        null=False,
    )
    objecttype = models.ForeignKey(
        ObjectType,
        on_delete=models.PROTECT,
        null=False,
        verbose_name="Object Type",
        # TODO: in the form, make subtype required if the selected type has > 0 subtypes
    )
    objectsubtype = models.ForeignKey(
        ObjectSubtype,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Object Subtype",
        # TODO: in the form, filter available subtypes by selected type
    )
    sealingfunction = models.CharField(
        max_length=20,
        choices=SEALINGFUNCTION_CHOICES,
        null=True,
        blank=True,
        # TODO: in the form, this becomes visible and required when subtype is "Sealing"
    )
    clayslaborsealingmarking = models.CharField(
        max_length=20,
        choices=CLAYSLABORSEALINGMARKING_CHOICES,
        null=True,
        blank=True,
        # TODO: in the form, this becomes visible and required when subtype is "Clay Slab" or "Sealing"
    )
    bladeserration = models.CharField(
        max_length=20,
        choices=BLADESERRATION_CHOICES,
        null=True,
        blank=True,
        # TODO: in the form, this becomes visible and required when subtype is "Blade"
    )
    preservation = models.CharField(
        max_length=20,
        choices=PRESERVATION_CHOICES,
        null=False,
    )
    repairedorrepurposed = models.CharField(
        max_length=25,
        choices=REPAIREDORREPURPOSED_CHOICES,
        null=False,
    )
    material = models.CharField(
        max_length=20,
        choices=MATERIAL_CHOICES,
        null=False,
    )
    stonesubtype = models.CharField(
        max_length=20,
        choices=STONESUBTYPE_CHOICES,
        null=True,
        blank=True,
        # TODO: in the form, this becomes visible and required when material is "Stone"
    )
    metalsubtype = models.CharField(
        max_length=20,
        choices=METALSUBTYPE_CHOICES,
        null=True,
        blank=True,
        # TODO: in the form, this becomes visible and required when material is "Metal"
    )
    maincolor = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        null=False,
    )
    decoration = models.CharField(
        max_length=20,
        choices=DECORATION_CHOICES,
        null=True,
        blank=True,
    )
    decorationcolor = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        null=True,
        blank=True,
    )
    height = models.CharField(
        max_length=35,
        null=True,
        blank=True,
    )
    length = models.CharField(
        max_length=35,
        null=True,
        blank=True,
    )
    width = models.CharField(
        max_length=35,
        null=True,
        blank=True,
    )
    thickness = models.CharField(
        max_length=35,
        null=True,
        blank=True,
    )
    diametermax = models.CharField(
        max_length=35,
        null=True,
        blank=True,
    )
    diametermin = models.CharField(
        max_length=35,
        null=True,
        blank=True,
    )
    diameterholes = models.CharField(
        max_length=35,
        null=True,
        blank=True,
    )
    description = models.TextField(
        null=True,
        blank=True,
    )
    notes = models.TextField(
        null=True,
        blank=True,
    )
    senttobaghdad = models.BooleanField(
        null=False,
        default=False,
    )
    baghdadnumber = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        # TODO: in the form, make this required if senttobaghdad is checked
    )
    tobephotographed = models.BooleanField(
        null=False,
        default=False,
    )
    photographed = models.BooleanField(
        null=False,
        default=False,
    )
    tobedrawn = models.BooleanField(
        null=False,
        default=False,
    )
    drawn = models.BooleanField(
        null=False,
        default=False,
    )
    voided = models.BooleanField(
        null=False,
        default=False,
    )

    class Meta:
        db_table = "lap_objects"
        verbose_name_plural = "Objects"
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(
                Lower("number"),
                name="unique_object_number",
                violation_error_message="This number already exists.",
            ),
        ]

    def __str__(self):
        return self.number

    def clean(self):
        if self.locale != self.su.locale:
            raise ValidationError("The Locale for this SU doesn’t match the Locale entered above.")
        if self.season != self.lot.season:
            raise ValidationError("The Season for this Lot doesn’t match the Season entered above.")
        if self.su != self.lot.su:
            raise ValidationError("The SU for this Lot doesn’t match the SU entered above.")
