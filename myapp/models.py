from django.db import models


# Create your models here.

class Subscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


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
