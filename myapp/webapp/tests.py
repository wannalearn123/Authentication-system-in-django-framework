from django.test import TestCase

# Create your tests here.
from django.core.mail import send_mail
send_mail('Test', 'Hello!', 'from@example.com', ['to@example.com'], fail_silently=False)
