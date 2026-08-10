from django import forms


class CustomImageWidget(forms.ClearableFileInput):
    template_name = "widgets/custom_image_widget.html"

class CustomWorldfileWidget(forms.ClearableFileInput):
    template_name = "widgets/custom_worldfile_widget.html"
