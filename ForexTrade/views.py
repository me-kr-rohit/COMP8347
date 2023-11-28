from urllib import request

import paypalrestsdk
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from pandas.io.formats import console
from paypalrestsdk import Payment
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.sites import requests
from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
from django.views import View
import requests
from django.core.exceptions import ValidationError
from django.http import JsonResponse
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
from COMP8347 import settings
from ForexTrade.models import UserProfile, Membership, Payment
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
        id_or_photo = request.FILES.get('id_or_photo')

        # Validate the file type
        allowed_file_types = ['image/jpeg', 'image/png']

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
                "error": "Invalid file type. Please upload a valid  photo (JPEG, PNG)."
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
                membership=default_membership,
                id_or_photo=id_or_photo,
                created_at=timezone.now()
            )

            messages.success(request, 'Registration successful!')
            messages.get_messages(request)
            storage = messages.get_messages(request)
            storage.used = True  # This line clears all existing messages
            return redirect('login')  # Redirect to the home page after successful registration
        except IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                print(f"Error: {e}")
                messages.error(request, 'Email already exists. Please try another email.')
                return render(request, 'register.html', {'error_message': 'An error occurred during registration.'})
            else:
                print(f"Unexpected error: {e}")
                messages.error(request, f'Error: {e}')
                return render(request, 'register.html', context={'error': f'Error saving the file: {e}'})
        except ValidationError as e:
            context = {
                "error": f"Error saving the file: {e}"
            }
            # Render the 'register.html' template with a specific error message
            return render(request, 'register.html', context=context)


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Use the correct parameters for authenticate based on your authentication backend
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page after successful login
        else:
            error_message = 'Invalid email or password.'
            messages.error(request, error_message)
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html', {})


class LogoutView(View):
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


# Below code added by Rohit Kumar - 110088741 : To fetch exchange rate from API
def get_exchange_rate(request):
    # Get parameters from the URL using request.GET
    currency_you_have = request.GET.get('currencyYouHave')
    currency_you_want = request.GET.get('currencyYouWant')
    amount = request.GET.get('amount')

    # API endpoint
    api_url = 'https://api.fxratesapi.com/latest'

    # Parameters for the API request
    params = {
        'base': currency_you_have,
        'currencies': currency_you_want,
        'amount': amount,
    }

    # Make the API call
    response = requests.get(api_url, params=params)

    # Check if the API call was successful
    if response.status_code == 200:
        data = response.json()
        converted_amount = data['rates'].get(currency_you_want, 0)

        return JsonResponse({'success': True, 'convertedAmount': converted_amount})
    else:
        # Handle the API error
        return JsonResponse({'success': False})


# Below code added by Rohit Kumar - 110088741 : To fetch the historical trend from an API

def trend(request):
    return render(request, 'trend.html')


def timeseries_view(request):
    # API endpoint
    api_url = 'https://api.fxratesapi.com/timeseries'
    end_date = request.POST.get('toDate')
    start_date = request.POST.get('fromDate')
    currency = request.POST.get('currencyYouWant')
    accuracy = 'day'

    # Parameters for the API request
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'currencies': currency,
        'accuracy': accuracy
    }

    # Make the API call
    response = requests.get(api_url, params=params)

    try:
        # Check if the API call was successful
        if response.status_code == 200:
            rates_data = response.json()["rates"]

            dates = [datetime.fromisoformat(date[:-1]) for date in rates_data.keys()]
            rates = [rate_data[currency] for rate_data in rates_data.values()]

            # Plot the graph
            plt.figure(figsize=(10, 6))
            # plt.plot(dates, rates, label="Exchange Rate")
            plt.plot(dates, rates, label="Exchange Rate", marker='o', linestyle='-')
            plt.title('Exchange Rate Historical Trend')
            plt.xlabel('Date')
            plt.ylabel('Exchange Rate')
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            plt.grid(True)

            # Save the plot to a BytesIO object
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            plt.close()

            # Encode the plot as base64
            plot_data = base64.b64encode(buffer.read()).decode('utf-8')
            buffer.close()

            context = {'plot_data': plot_data}
            return render(request, 'trend_chart.html', context)

    except Exception as e:
        # Handle exceptions
        return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})


def get_paypal_api():
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_SECRET,
    })
    return paypalrestsdk


# Below code added by Rohit Kumar - 110088741 : To fetch the payment details


def payment_view(request):
    try:
        # total_amount = float(total_amount)
        amount = request.POST.get('amount')
        total_amount = float(amount)
    except ValueError:
        # Handle the case where total_amount is not a valid float
        # You might want to redirect or display an error message
        pass

    paypal_client_id = settings.PAYPAL_CLIENT_ID
    # paypal_secret = settings.PAYPAL_SECRET

    paypal_api = get_paypal_api()

    # Create a PayPal payment
    payment = paypal_api.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "transactions": [
            {
                "amount": {
                    "total": str(total_amount),
                    "currency": "USD",
                },
            },
        ],
        "redirect_urls": {
            "return_url": "http://localhost:8000/payment_success/",
            "cancel_url": "http://localhost:8000/payment_cancel/",
        },
    })

    if payment.create():
        # Save the payment details to your local Payment model
        Payment.objects.create(
            user=request.user,
            amount=total_amount,
            payment_date=timezone.now(),
            transaction_id=payment.id,
        )
        print(Payment)
    else:
        print(payment.error)
        # Handle payment creation error

    return render(request, 'payment.html',
                  {'paypal_client_id': paypal_client_id, 'total_amount': total_amount})


def payment_success(request):
    return render(request, 'payment_success.html')


@login_required
def Payment_History(request):
    payments = Payment.objects.all()
    context = {'payments': payments}
    return render(request, 'Payment_History.html', context)


# End by Rohit Kumar - 110088741
@login_required
def account_settings(request):
    # Get the UserProfile associated with the logged-in user
    user_profile = get_object_or_404(UserProfile, user=request.user)

    context = {
        'user_profile': user_profile,
    }

    return render(request, 'my_account.html', context=context)

