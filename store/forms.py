from django import forms
from .models import QRCode
from .models import Customization, CustomFormField, CustomForm


class QRCodeForm(forms.ModelForm):
    class Meta:
        model = QRCode
        fields = ['url', 'selected_for_card']


class QRCodeForm(forms.ModelForm):
    class Meta:
        model = QRCode
        fields = ['url', 'selected_for_card']

def get_custom_form_for_product(product, instance=None, require_all_fields=False):
    try:
        custom_form = product.custom_form
        if not custom_form:
            return None
    except CustomForm.DoesNotExist:
        return None

    class DynamicForm(forms.ModelForm):
        class Meta:
            model = Customization
            fields = []

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            data = instance.data if instance and instance.data else {}

            for field in custom_form.fields.all():
                required = require_all_fields
                initial = data.get(field.label)

                if field.field_type == 'text':
                    self.fields[field.label] = forms.CharField(
                        label=field.label,
                        required=required,
                        initial=initial
                    )
                elif field.field_type == 'textarea':
                    self.fields[field.label] = forms.CharField(
                        widget=forms.Textarea,
                        label=field.label,
                        required=required,
                        initial=initial
                    )
                elif field.field_type == 'file':
                    self.fields[field.label] = forms.FileField(
                        label=field.label,
                        required=required
                    )

    return DynamicForm(instance=instance)
