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


class Role(TimestampedModel):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class UserProfile(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, unique=True)
    # New fields
    first_name = models.CharField(max_length=30, default='')  # You can set a default value here
    last_name = models.CharField(max_length=30)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, default=3)
    id_or_photo = models.FileField(upload_to='user_uploads/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        role_name = self.role.name if self.role else "No Role"
        membership_name = self.membership.name if self.membership else "No Membership"
        return f"Role: {role_name}, Membership: {membership_name},FirstName: {self.first_name}, LastName: {self.last_name},Email: {self.email}"
