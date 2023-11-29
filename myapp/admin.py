from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import Subscription, ContactMessage, GlossaryTerm,  Payment

admin.site.register(Subscription)
admin.site.register(ContactMessage)
admin.site.register(GlossaryTerm)
admin.site.register(Payment)
