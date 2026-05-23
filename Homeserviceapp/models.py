from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class Login(AbstractUser):
    is_user = models.BooleanField(default=False)
    is_worker = models.BooleanField(default=False)


class UserRegistration(models.Model):
    user = models.OneToOneField(Login, on_delete=models.CASCADE, related_name='user')
    name = models.CharField(max_length=250)
    address = models.TextField(max_length=300)
    contact = models.IntegerField()


class Category(models.Model):
    category = models.CharField(max_length=300)

    def __str__(self):
        return self.category


class WorkerRegistration(models.Model):
    user = models.OneToOneField(Login, on_delete=models.CASCADE, related_name='worker')
    name = models.CharField(max_length=300)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    address = models.TextField()
    contact = models.IntegerField()
    paypal_email = models.CharField(max_length=200, null=True, blank=True)
    payment = models.IntegerField(null=True, blank=True)
    experience = models.IntegerField()
    image = models.ImageField(upload_to='uploads/')


class Availability(models.Model):
    user = models.ForeignKey(WorkerRegistration, on_delete=models.DO_NOTHING)
    date = models.DateField()
    time = models.TimeField()
    booking_status = models.BooleanField(default=False)

    def __str__(self):
        return self.date,self.time


class Appointment(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='appointment')
    user_profile = models.ForeignKey(UserRegistration, on_delete=models.CASCADE, related_name='user_profile')
    worker = models.ForeignKey(WorkerRegistration, on_delete=models.CASCADE, related_name='worker')
    availability = models.ForeignKey(Availability, on_delete=models.DO_NOTHING)
    appointment_status = models.IntegerField(default=0)
    work_status = models.BooleanField(default=False)
    payment_status=models.IntegerField(default=0)
    worker_amount=models.IntegerField(null=True,blank=True)
    worker_payment_status=models.IntegerField(default=0)
    admin_wallet=models.IntegerField(null=True,blank=True)


class Feedback(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='feedback')
    date = models.DateField()
    name = models.CharField(max_length=300)
    complaint = models.TextField()
    reply = models.TextField(null=True, blank=True)


class Payment(models.Model):
    user = models.ForeignKey(UserRegistration, on_delete=models.DO_NOTHING,related_name='payment')
    booking = models.ForeignKey(Appointment, on_delete=models.DO_NOTHING)
    worker = models.ForeignKey(WorkerRegistration, on_delete=models.DO_NOTHING,related_name='payment_worker')
    date=models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=200, default="paypal")
    order_id = models.CharField(max_length=255, blank=True, null=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)


class WorkerEarnings(models.Model):
    worker = models.ForeignKey(WorkerRegistration, on_delete=models.DO_NOTHING,related_name='worker_payment')
    booking = models.ForeignKey(Appointment, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=200, default="paypal")
    order_id = models.CharField(max_length=255, blank=True, null=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)

