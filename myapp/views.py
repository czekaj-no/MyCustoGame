from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from .forms import ContactForm


def home(request):
    return render(request, 'home.html')

def nasze_gry (request):
    return render (request, 'nasze-gry.html')

def personalizuj_gre (request):
    return render (request, 'personalizuj-gre.html')

def moje_konto (request):
    return render (request, 'moje-konto.html')

def b2b (request):
    return render (request, 'b2b.html')

def galeria (request):
    return render (request, 'galeria.html')

def b2b_meeting (request):
    return render (request, 'b2b_meeting.html')

from django.core.mail import send_mail
from django.shortcuts import render
from django.conf import settings

def kontakt(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        full_message = f"Wiadomość od: {name} ({email})\n\nTreść:\n{message}"

        # Uzupełnij te dane przed opublikowaniem strony!
        send_mail(
            subject="Wiadomość z formularza kontaktowego MyCustoGame",
            message=full_message,
            from_email="twoj_email@gmail.com",
            recipient_list=["odbiorca@gmail.com"],
            fail_silently=False,
        )

    return render(request, "kontakt.html")



