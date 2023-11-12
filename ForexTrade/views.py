

from django.contrib import messages
import logging
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.core.exceptions import ValidationError

from ForexTrade.models import Role, UserProfile, Membership


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
        username = first_name + " " + last_name
        if password != confirm_password:
            context = {
                "error": "Passwords do not match."
            }
            return render(request, 'register.html', context=context)
        existing_user = User.objects.filter(Q(email=email)).first()
        context = {"error": None}
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

        # Create a new User object
        user = User.objects.create_user(username=username, email=email, password=password)

        try:
            # Get the Role object based on the selected role
            role_obj = Role.objects.get(name=role)
        except Role.DoesNotExist:
            # Handle the case where the role doesn't exist
            # You can choose to create the role or raise an Http404 exception or return an error message
            role_obj = None  # Set role_obj to None or handle it according to your application's logic
        if role_obj is None:
            # Create the role if it doesn't exist
            role_obj = Role.objects.create(name=role)
        try:
            # Get the default Membership object
            default_membership, created = Membership.objects.get_or_create(
                pk=3,  # Assuming 3 is the default membership ID
                defaults={'name': 'Default', 'price': 0.0, 'currency': 'USD'}
            )
        except Membership.DoesNotExist:
            # Handle the case where the membership doesn't exist
            # You can choose to create the membership or raise an Http404 exception or return an error message
            default_membership = None  # Set default_membership to None or handle it according to your application's logic

        if default_membership is None:
            # Create the default membership if it doesn't exist
            default_membership = Membership.objects.create(pk=3, name='Default', price=0.0, currency='USD')

        try:
            # Create a UserProfile object with the uploaded file
            user_profile = UserProfile.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role_obj,  # Set the role object here
                membership=default_membership,
                id_or_photo=id_or_photo,
                created_at=timezone.now())
            messages.success(request, 'Registration successful!')  # Add success message
        except ValidationError as e:
            context = {
                "error": f"Error saving the file: {e}"
            }
            return render(request, 'register.html', context=context)

            # Clear the form by rendering the registration page again
        return render(request, 'register.html', {'success_message': 'Registration successful!'})


def login_view(request):
  #  if request.user.is_authenticated:
   #     return redirect('home')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)
        print(f"Email: {email}, Password: {password},Auth:{user}")
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            #return redirect('register')  # Redirect to the home page after successful login
        else:
            error_message = 'Invalid email or password.'
            messages.error(request, error_message)
            #return render(request, 'login.html', {'error_message': error_message})

        return render(request, 'login.html')
    else:
        return render(request, 'login.html')
