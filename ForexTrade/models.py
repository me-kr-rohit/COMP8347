from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Membership(TimestampedModel):
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    currency = models.CharField(max_length=3)

    def __str__(self):
        return f"Name: {self.name}, Price: {self.price}, Currency: {self.currency}"


class UserProfile(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, unique=True)
    # New fields
    first_name = models.CharField(max_length=30, default='')  # You can set a default value here
    last_name = models.CharField(max_length=30)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, default=3)
    id_or_photo = models.FileField(upload_to='user_uploads/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        membership_name = self.membership.name if self.membership else "No Membership"
        return f"Membership: {membership_name},FirstName: {self.first_name}, LastName: {self.last_name},Email: {self.email}"


# Below code added by Rohit Kumar - 110088741
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=50)


class PaymentHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10)  # 'buy' or 'sell'
    transaction_date = models.DateTimeField(auto_now_add=True)


# End by Rohit Kumar - 110088741

# Start by Abhirup Ranjan - 110091866
class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    pin_code = models.CharField(max_length=10)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"Address for {self.user.username}"

# End by Abhirup Ranjan - 110091866
