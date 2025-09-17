# projects/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse
from django.shortcuts import render, redirect
from .models import Project, Feedback, Achievement
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponse
# from docx import Document
from potfolio_app.models import Project  # Replace with your model
from django.http import HttpResponse
# from docx import Document
from .models import Project  # Adjust the import based on your app's name

def export_to_word(request):
    return response


def home(request):
    projects = Project.objects.all().order_by('-created_at')

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and subject and message:
            Feedback.objects.create(name=name, email=email, subject=subject, message=message)
            try:
                full_message = f"From: {name} <{email}>\n\n{message}"
                send_mail(
                    subject=subject,
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=["emmanuelcharles362@gmail.com"],
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent successfully.")
            except BadHeaderError:
                messages.error(request, "Invalid header found.")
            except Exception:
                messages.error(request, "There was an error sending your message. Please try again later.")
            return redirect('home')

    achievements = Achievement.objects.filter(is_active=True)
    return render(request, 'projects/home.html', {'projects': projects, 'achievements': achievements})

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)

    return render(request, 'projects/project_detail.html', {'project': project})

from django.contrib.auth.decorators import login_required

@login_required
def download_file(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if project.download_file:
        return FileResponse(project.download_file.open(), as_attachment=True)
    return redirect('home')

from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'projects/register.html', {'form': form})
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import HttpResponseRedirect

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "projects/login.html")
