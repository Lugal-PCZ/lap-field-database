from django.db import models
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from django.utils import timezone

from django_advance_thumbnail import AdvanceThumbnailField

from accounts.models import CustomUser
from lapinfo.models import Season
from contexts.models import SU
from lots.models import Lot


def get_next_object_number(selectedseason=None):
    currentseason = Season.objects.order_by("id").last().name  # type: ignore
    if selectedseason and selectedseason != currentseason:
        # with the dummy data, this will throw an error for 1LAP. It can safely be ignored
        # there are no cataloged 2LAP objects, so if we were to retroactively do one, we know the starting number
        if selectedseason == "2LAP":
            nextnumber = "2LAP00000"
        else:
            lastnumber = Object.objects.filter(season__name=selectedseason).order_by("number").last().number  # type: ignore
            nextnumber = f"{selectedseason}{int(lastnumber.split('LAP')[1]) + 1:05d}"
    else:
        lastnumber = Object.objects.all().order_by("number").last().number  # type: ignore
        if lastnumber.split("LAP")[0] != currentseason.split("LAP")[0]:
            nextnumber = f"{currentseason}{int(currentseason.split('LAP')[0]) - 3:02d}000"
        else:
            nextnumber = f"{currentseason}{int(lastnumber.split('LAP')[1]) + 1:05d}"
    return nextnumber


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
        return self.name

    def formatted_name(self):
        return f"{self.name} ({self.type})"


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
    SHELLSUBTYPE_CHOICES = [
        ("Bivalve", "Bivalve"),
        ("Gastropod", "Gastropod"),
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
        default=get_next_object_number,
        null=False,
    )
    excavationnumber = models.CharField(
        max_length=15,
        default=Season.objects.last().name,  # type: ignore
        null=False,
        verbose_name="Excavation Number",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        default=Season.objects.last().pk,  # type: ignore
        null=False,
    )
    su = models.ForeignKey(
        SU,
        on_delete=models.PROTECT,
        null=False,
        verbose_name="SU or 1LAP/3LAP Locus",
    )
    surfacefind = models.BooleanField(
        null=False,
        default=False,
        verbose_name="Surface Find (no Lot)",
    )
    lot = models.ForeignKey(
        Lot,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
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
    objecttype = models.ForeignKey(
        ObjectType,
        on_delete=models.PROTECT,
        null=False,
        verbose_name="Object Type",
    )
    objectsubtype = models.ForeignKey(
        ObjectSubtype,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Object Subtype",
    )
    sealingfunction = models.CharField(
        max_length=20,
        choices=SEALINGFUNCTION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Sealing Function",
    )
    clayslaborsealingmarking = models.CharField(
        max_length=20,
        choices=CLAYSLABORSEALINGMARKING_CHOICES,
        null=True,
        blank=True,
        verbose_name="Clay Slab or Sealing Marking",
    )
    bladeserration = models.CharField(
        max_length=20,
        choices=BLADESERRATION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Blade Serration",
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
        verbose_name="Repaired/Repurposed",
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
        verbose_name="Stone Subtype",
    )
    metalsubtype = models.CharField(
        max_length=20,
        choices=METALSUBTYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Metal Subtype",
    )
    shellsubtype = models.CharField(
        max_length=20,
        choices=SHELLSUBTYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Shell Subtype",
    )
    maincolor = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        null=False,
        verbose_name="Main Color",
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
        verbose_name="Decoration Color",
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
        verbose_name="Diameter (max)",
    )
    diametermin = models.CharField(
        max_length=35,
        null=True,
        blank=True,
        verbose_name="Diameter (min)",
    )
    diameterholes = models.CharField(
        max_length=35,
        null=True,
        blank=True,
        verbose_name="Diameter (holes)",
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
        verbose_name="Sent to Baghdad",
    )
    baghdadnumber = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Baghdad Number",
    )
    published = models.BooleanField(
        null=False,
        default=False,
        verbose_name="Published",
    )
    publicationcitations = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Publication Citations",
    )
    tobephotographed = models.BooleanField(
        null=False,
        default=True,
        verbose_name="To Be Photographed",
    )
    photographed = models.BooleanField(
        null=False,
        default=False,
    )
    tobedrawn = models.BooleanField(
        null=False,
        default=False,
        verbose_name="To Be Drawn",
    )
    drawn = models.BooleanField(
        null=False,
        default=False,
    )
    voided = models.BooleanField(
        null=False,
        default=False,
    )
    image = models.FileField(
        upload_to="uploads/objects/images/",
        null=True,
        blank=True,
    )
    image_thumbnail = AdvanceThumbnailField(
        source_field="image",  # type: ignore
        upload_to="uploads/objects/images/thumbnails/",
        size=(150, 100),  # type: ignore
        null=True,
        blank=True,
    )
    image_onscreen = AdvanceThumbnailField(
        source_field="image",  # type: ignore
        upload_to="uploads/objects/images/onscreen/",
        size=(310, 310),  # type: ignore
        null=True,
        blank=True,
    )
    image_pdf = AdvanceThumbnailField(
        source_field="image",  # type: ignore
        upload_to="uploads/objects/images/pdf/",
        size=(600, 600),  # type: ignore
        null=True,
        blank=True,
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
        # if f"{self.number.split('LAP')[0]}LAP" != str(self.season):
        #     raise ValidationError("The number given to this Object doesn’t match the Season.")
        # if self.excavationnumber.upper() != "N/A" and f"{self.number.split('LAP')[0]}LAP" != str(self.season):
        #     raise ValidationError("The excavationnumber given to this Object doesn’t match the Season.")
        if self.lot and f"{str(self.lot).split('LAP')[0]}LAP" != str(self.season):
            raise ValidationError("The lot given to this Object doesn’t match the Season.")

    def save(self, *args, **kwargs):
        self.excavationnumber = self.excavationnumber.upper()
        super(Object, self).save(*args, **kwargs)
