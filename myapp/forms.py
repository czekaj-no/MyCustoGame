from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(label="Imię i nazwisko", max_length=100)
    email = forms.EmailField(label="Adres e-mail")
    message = forms.CharField(label="Wiadomość", widget=forms.Textarea)
