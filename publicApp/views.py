
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings

def home(request):
    role = request.session.get('role', 'guest')
    data = {'role': role}
    return render(request, 'home.html', data)

def about(request):
    role = request.session.get('role', 'guest')
    data = {'role': role}
    return render(request, 'about.html', data)

def services(request):
    role = request.session.get('role', 'guest')
    data = {'role': role}
    return render(request, 'services.html', data)



def contact(request):
    
    role = request.session.get('role', 'guest')
    
    # related to sending an email in Contact Page.

    if request.method == "POST":
        
        import json
        try:
            data = json.loads(request.body)
            name = data.get("name")
            email = data.get("email")
            message = data.get("message")

            
            send_mail(
                subject=f"A New Message from {name}",
                message=message,
                from_email=email,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )

            return JsonResponse({"success": True})
        except Exception as error:
            return JsonResponse({"success": False, "error": str(error)})

    
    return render(request, "contact.html", {"role": role})

def store_page(request):
    role = request.session.get('role', 'guest')
    data = {'role': role}
    
    return render(request, 'store.html', data)
