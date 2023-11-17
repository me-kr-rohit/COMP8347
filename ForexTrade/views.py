from django.contrib import messages
import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.core.exceptions import ValidationError

from ForexTrade.models import Role, UserProfile, Membership
# views.py
from django.shortcuts import render


def home_view(request):
    return render(request, 'home.html')


# Create your views here.
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        role = request.POST['role']
        id_or_photo = request.FILES.get('id_or_photo')

        # Validate the file type
        allowed_file_types = ['image/jpeg', 'image/png', 'application/pdf']

        if password != confirm_password:
            context = {
                "error": "Passwords do not match."
            }
            return render(request, 'register.html', context=context)

        existing_user = UserProfile.objects.filter(Q(email=email)).first()

        if existing_user:
            context = {
                "error": "Email already exists!"
            }
            return render(request, 'register.html', context=context)

        if id_or_photo and id_or_photo.content_type not in allowed_file_types:
            context = {
                "error": "Invalid file type. Please upload a valid ID or photo (JPEG, PNG, PDF)."
            }
            return render(request, 'register.html', context=context)

        try:
            # Create a new User object
            user = User.objects.create_user(email, email, password)
            # Authenticate the user
            authenticate_user = authenticate(request, email=email, password=password)
            if authenticate_user:
                login(request, authenticate_user)
            else:
                messages.error(request, 'Error during user authentication.')

            # Get or create the Role object based on the selected role
            role_obj, created = Role.objects.get_or_create(name=role)

            # Get or create the default Membership object
            default_membership, created = Membership.objects.get_or_create(
                pk=3,  # Assuming 3 is the default membership ID
                defaults={'name': 'Default', 'price': 0.0, 'currency': 'USD'}
            )

            # Create a new UserProfile object
            user_profile = UserProfile.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role_obj,
                membership=default_membership,
                id_or_photo=id_or_photo,
                created_at=timezone.now()
            )

            messages.success(request, 'Registration successful!')
            return render(request, 'home.html')  # Redirect to the home page after successful registration
        except IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                print(f"Error: {e}")
                messages.error(request, 'Email already exists. Please try another email.')
            else:
                print(f"Unexpected error: {e}")
                messages.error(request, f'Error: {e}')

        except ValidationError as e:
            context = {
                "error": f"Error saving the file: {e}"
            }
            return render(request, 'register.html', context=context)


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Use the correct parameters for authenticate based on your authentication backend
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')  # Redirect to the home page after successful login
        else:
            error_message = 'Invalid email or password.'
            messages.error(request, error_message)
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')


class LogoutView:
    def get(self, request):
        logout(request)  # Call the logout function to log out the user
        messages.success(request, 'Logout successful!')
        return redirect('home')  # Redirect to the home page after successful logout


# Abhirup Start
def about(request):
    return render(request, 'aboutUs.html')


def faq(request):
    return render(request, 'faq.html')


def offers(request):
    return render(request, 'offers.html')


def contact(request):
    return render(request, 'contactUs.html')
# Abhirup End
