from django.db import models

class Subscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

# Create your models here.




class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class GlossaryTerm(models.Model):
    term = models.CharField(max_length=255, unique=True)
    definition = models.TextField()

    def __str__(self):
        return self.term


class Payment(models.Model):
    name = models.CharField(max_length=255)
    currency = models.CharField(max_length=50)
    destination = models.CharField(max_length=255)
    debited = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    exchangement = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    province = models.CharField(max_length=100)
    region = models.CharField(max_length=100)




    def __str__(self):
        return f"{self.name} - {self.timestamp}"

class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Province(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Region(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    currency_code = models.CharField(max_length=3)  # Example: USD, CAD, etc.

    def __str__(self):
        return self.name

# Create your models here.
class PaymentHistory(models.Model):
    name = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    debited = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default="completed")
    currency = models.CharField(max_length=3, default="INR")
    exchangedamt = models.CharField(max_length=255)
    pickuplocation = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    region = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}'s Transaction ({self.created_at})"
