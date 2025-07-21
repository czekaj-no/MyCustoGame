from django import forms
from .models import QRCode
from .models import Customization, CustomFormField, CustomForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate



class CustomClearableFileInput(ClearableFileInput):
    initial_text = _("Obecny plik:")
    input_text = _("Wybierz plik")
    clear_checkbox_label = _("Usuń plik")

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

            self._custom_file_fields = []

            for field in custom_form.fields.all():
                required = require_all_fields
                initial = data.get(field.label, "")

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
                        required=required,
                        widget=CustomClearableFileInput
                    )
                    self._custom_file_fields.append(field.label)

                    # 🟡 PRZYWRÓĆ POPRZEDNI PLIK DO POLA FILE
                    if instance:
                        existing_file = instance.files.filter(label=field.label).first()
                        if existing_file:
                            self.initial[field.label] = existing_file.file

    return DynamicForm(instance=instance)


class LoginOrEmailAuthenticationForm(forms.Form):
    username_or_email = forms.CharField(label='Login lub email')
    password = forms.CharField(widget=forms.PasswordInput, label='Hasło')

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        # Spróbuj znaleźć użytkownika po loginie
        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            # Jeśli nie znaleziono, spróbuj po emailu
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                user = None

        if user:
            authenticated_user = authenticate(username=user.username, password=password)
            if authenticated_user:
                self.user = authenticated_user
                return cleaned_data

        raise forms.ValidationError("Nieprawidłowy login/email lub hasło.")

    def get_user(self):
        return getattr(self, 'user', None)


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'id': 'id_username'})
        self.fields['password'].widget.attrs.update({'id': 'id_password'})

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Adres email')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'id': 'username'})
        self.fields['email'].widget.attrs.update({'id': 'email'})
        self.fields['password1'].widget.attrs.update({'id': 'password1'})
        self.fields['password2'].widget.attrs.update({'id': 'password2'})