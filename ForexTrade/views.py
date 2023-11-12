from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
import requests

from ForexTrade.models import Role, UserProfile


# Create your views here.
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def get(self, request):
        return render(request, 'exchange_rate_input.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']
        existing_user = User.objects.filter(Q(username=username) | Q(email=email)).first()
        context = {"error": None}
        if existing_user:
            context = {
                "error": "username or email already exists!"
            }
            return render(request, 'register.html', context=context)
        # Create a new User object
        user = User.objects.create_user(username=username, email=email, password=password)

        # Get the Role object based on the selected role
        role_obj = Role.objects.get(name=role)

        # Create a UserProfile object
        UserProfile.objects.create(user=user, role=role_obj)
        return redirect('home')  # Redirect to the home page after successful registration

        return render(request, 'register.html', context=context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page after successful login
        else:
            error_message = 'Invalid username or password.'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')


def exchange_rate_view(request):
    print("request GET: ", request.GET)
    # Get parameters from the URL using request.GET
    currencies = request.GET.get('currencies')
    base_currency = request.GET.get('base')
    amount = request.GET.get('amount')

    # API endpoint
    api_url = 'https://api.fxratesapi.com/latest'

    # Parameters for the API request
    params = {
        'currencies': currencies,
        'base': base_currency,
        'amount': amount,
    }

    # Make the API call
    response = requests.get(api_url, params=params)

    # Check if the API call was successful
    if response.status_code == 200:
        data = response.json()
        # Process the data as needed
        context = {
            'base_currency': data['base'],
            'target_currency': currencies,
            'exchange_rate': data['rates'].get(currencies, 0),
            'amount': amount,
        }
        print("context:", context)
        return render(request, 'exchange_rate.html', context)
    else:
        # Handle the API error
        return render(request, 'error.html')
