from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(label="Imię i nazwisko", max_length=100)
    email = forms.EmailField(label="Adres e-mail", max_length=100)
    message = forms.CharField(label="Wiadomość", widget=forms.Textarea, max_length=100)
