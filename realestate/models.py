from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class User(AbstractUser, TimestampedModel):

    def __str__(self):
        return self.get_full_name() or self.username

class Property(TimestampedModel):
    DISTRICT_CHOICES = [
        ("Famagusta", "Famagusta"),
        ("Kyrenia", "Kyrenia"),
        ("Larnaca", "Larnaca"),
        ("Limassol", "Limassol"),
        ("Nicosia", "Nicosia"),
        ("Paphos", "Paphos"),
    ]
    title = models.CharField(max_length=256)
    district = models.CharField(max_length=20, choices=DISTRICT_CHOICES)
    estimated_value = models.DecimalField(max_digits=15, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="properties")

    def __str__(self):
        return self.title



class Transaction(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="transactions")
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(100.00)]
    )
    price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(10000)])
    transaction_date = models.DateTimeField()

    class Meta:
        unique_together = ("user", "property", "transaction_date")

    def __str__(self):
        return f"{self.user} - {self.property} ({self.percentage}%)"


