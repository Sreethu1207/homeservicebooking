import uuid

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from Homeserviceapp.form import UserRegistrationForm, LoginForm, CategoryForm, WorkerRegistrationForm, AvailabilityForm, \
    FeedbackForm
from Homeserviceapp.models import Category, WorkerRegistration, Availability, UserRegistration, Appointment, Feedback, \
    Payment, WorkerEarnings
from Homeserviceapp.paypal_utils import get_paypal_access_token


# Create your views here.


def main_view(request):
    return render(request, 'index.html')


def user_registration(request):
    login_form = LoginForm()
    user_form = UserRegistrationForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        user_form = UserRegistrationForm(request.POST)
        if login_form.is_valid() and user_form.is_valid():
            user = login_form.save(commit=False)
            user.is_user = True
            user.save()
            c = user_form.save(commit=False)
            c.user = user
            c.save()
            return redirect('login_view')
    return render(request, 'UserRegistration.html', {'login_form': login_form, 'user_form': user_form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pass')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_user:
                return redirect('user_dashboard')
            elif user.is_worker:
                return redirect('worker_dashboard')
            elif user.is_staff:
                return redirect('admin_dashboard')
        else:
            messages.info(request, 'invalid credentials')
    return render(request, 'login.html')


def user_dashboard(request):
    return render(request, 'user/user_dashboard.html')


def worker_dashboard(request):
    return render(request, 'worker/worker_dashboard.html')


def admin_dashboard(request):
    return render(request, 'admin/admin_dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login_view')


def category_add(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'service category added successfully')
            return redirect('category_add')
    return render(request, 'admin/category_add.html', {'form': form})


def category_view(request):
    data = Category.objects.all()
    return render(request, 'admin/category_view.html', {'data': data})


def category_delete(request, id):
    data = Category.objects.get(id=id)
    data.delete()
    return redirect('category_view')


def user_category_view(request):
    data = Category.objects.all()
    return render(request, 'user/user_category_view.html', {'data': data})


def worker_registration(request):
    login_form = LoginForm()
    worker_form = WorkerRegistrationForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        worker_form = WorkerRegistrationForm(request.POST, request.FILES)
        if login_form.is_valid() and worker_form.is_valid():
            user = login_form.save(commit=False)
            user.is_worker = True
            user.save()
            c = worker_form.save(commit=False)
            c.user = user
            c.save()
            return redirect('login_view')
    return render(request, 'WorkerRegistration.html', {'login_form': login_form, 'worker_form': worker_form})


def view_workers_user(request):
    data = WorkerRegistration.objects.all()
    return render(request, 'user/view_workers_user.html', {'data': data})


def view_workers_admin(request):
    data = WorkerRegistration.objects.all()
    return render(request, 'admin/view_workers_admin.html', {'data': data})


def worker_delete(request, id):
    data = WorkerRegistration.objects.get(id=id)
    data.delete()
    return redirect('view_workers_admin')


def update_payment(request, id):
    data = WorkerRegistration.objects.get(id=id)
    if request.method == 'POST':
        p = request.POST.get('payment')
        data.payment = p
        data.save()
        messages.info(request, 'Payment added')
        return redirect('view_workers_admin')
    return render(request, 'admin/add_payment.html', {'data': data})


def add_availability(request):
    form = AvailabilityForm()
    worker = request.user
    data = WorkerRegistration.objects.get(user=worker)
    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = data
            obj.save()
            messages.info(request, 'Availability added')
            return redirect('view_availability')
    return render(request, 'worker/add_availability.html', {'form': form})


def view_availability(request):
    today = timezone.now().date()
    worker = WorkerRegistration.objects.get(user=request.user)
    data = Availability.objects.filter(user=worker, date__gte=today).order_by('date', 'time')
    return render(request, 'worker/view_availability.html', {'data': data})


def delete_availability(request, id):
    data = Availability.objects.get(id=id)
    data.delete()
    return redirect('view_availability')


def update_availability(request, id):
    data = Availability.objects.get(id=id)
    form = AvailabilityForm(instance=data)
    if request.method == 'POST':
        form = AvailabilityForm(request.POST, instance=data)
        if form.is_valid():
            form.save()
            messages.info(request, 'Availability updated Successfully')
            return redirect('view_availability')
    return render(request, 'worker/update_availability.html', {'form': form})


def view_availability_user(request, id):
    today = timezone.now().date()
    worker = WorkerRegistration.objects.get(id=id)
    data = Availability.objects.filter(user=worker, date__gte=today).order_by('date', 'time')
    return render(request, 'user/view_worker_availability.html', {'data': data})


def book_appointment(request, id):
    availability = Availability.objects.get(id=id)
    u = UserRegistration.objects.get(user=request.user)
    worker = availability.user

    if availability.booking_status:
        messages.info(request, 'Appointment already exists')
        return redirect('view_worker_availability', worker.id)
    else:
        if request.method == 'POST':
            obj = Appointment()
            obj.user = u.user
            obj.user_profile = u
            obj.worker = worker
            obj.availability = availability
            obj.save()
            availability.booking_status = True
            availability.save()
            messages.info(request, 'Appointment booked successfully')
            return redirect('user_view_appointment')
    return render(request, 'user/book_appointment.html', {'availability': availability, 'worker': worker})


def user_view_appointments(request):
    u = UserRegistration.objects.get(user=request.user)
    data = Appointment.objects.filter(user=u.user)
    return render(request, 'user/booking_details.html', {'data': data})


def cancel_appointment(request, id):
    data = Appointment.objects.get(id=id)
    data.delete()
    return redirect('user_view_appointment')


def admin_view_appointment(request):
    data = Appointment.objects.all()
    return render(request, 'admin/admin_view_appointment.html', {'data': data})


def approve_appointment(request, id):
    data = Appointment.objects.get(id=id)
    data.appointment_status = 1
    data.save()
    return redirect('admin_view_appointment')


def reject_appointment(request, id):
    data = Appointment.objects.get(id=id)
    data.appointment_status = 2
    data.save()
    return redirect('admin_view_appointment')


def worker_view_appointment(request):
    w = WorkerRegistration.objects.get(user=request.user)
    data = Appointment.objects.filter(appointment_status=1, worker=w)
    return render(request, 'worker/view_works.html', {'data': data})


@login_required
def update_work_status(request, id):
    data = Appointment.objects.get(id=id)
    data.work_status = True
    data.save()
    return redirect('worker_view_appointment')


@login_required
def worker_completed_works(request):
    w = WorkerRegistration.objects.get(user=request.user)
    data = Appointment.objects.filter(work_status=True, worker=w)
    return render(request, 'worker/completed_works.html', {'data': data})


def admin_completed_works(request):
    data = WorkerRegistration.objects.all()
    return render(request, 'admin/completed_works1.html', {'data': data})


def list_completed_work(request, id):
    worker = WorkerRegistration.objects.get(id=id)
    data = Appointment.objects.filter(work_status=True, worker=worker)
    for item in data:
        item.worker_amount = worker.payment * 0.80
        item.save()
    return render(request, 'admin/completed_work2.html', {'data': data})


def add_complaints(request):
    form = FeedbackForm()
    u = request.user
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = u
            obj.save()
            messages.info(request, 'complaint registered successfully')
            return redirect('add_complaints')
    return render(request, 'user/add_complaints.html', {'form': form})


def view_complaints(request):
    data = Feedback.objects.filter(user=request.user)
    return render(request, 'user/view_complaints.html', {'data': data})


def delete_complaints(request, id):
    data = Feedback.objects.get(id=id)
    data.delete()
    return redirect('view_complaints')


def admin_view_complaints(request):
    data = Feedback.objects.all()
    return render(request, 'admin/admin_view_complaints.html', {'data': data})


def complaint_reply(request, id):
    data = Feedback.objects.get(id=id)
    if request.method == 'POST':
        r = request.POST.get('reply')
        data.reply = r
        data.save()
        messages.info(request, 'reply send for complaint')
        return redirect('admin_view_complaints')
    return render(request, 'admin/complaint_reply.html', {'data': data})


def worker_view_complaints(request):
    data = Feedback.objects.all()
    return render(request, 'worker/view_complaints.html', {'data': data})


def user_profile(request):
    data = UserRegistration.objects.filter(user=request.user)
    return render(request, 'user/user_profile.html', {'data': data})


def update_user_profile(request):
    data = UserRegistration.objects.get(user=request.user)
    form = UserRegistrationForm(instance=data)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, instance=data)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    return render(request, 'user/update_user_profile.html', {'form': form})


def worker_profile(request):
    data = WorkerRegistration.objects.filter(user=request.user)
    return render(request, 'worker/worker_profile.html', {'data': data})


def update_worker_profile(request):
    data = WorkerRegistration.objects.get(user=request.user)
    form = WorkerRegistrationForm(instance=data)
    if request.method == 'POST':
        form = WorkerRegistrationForm(request.POST, request.FILES, instance=data)
        if form.is_valid():
            form.save()
            return redirect('worker_profile')
    return render(request, 'worker/update_worker_profile.html', {'form': form})


def view_users(request):
    data = UserRegistration.objects.all()
    return render(request, 'admin/view_users.html', {'data': data})


def service_filter(request, id):
    category = Category.objects.get(id=id)
    data = WorkerRegistration.objects.filter(category=category)
    return render(request, 'user/service_filter.html', {'data': data})


def admin_service_filter(request, id):
    category = Category.objects.get(id=id)
    data = WorkerRegistration.objects.filter(category=category)
    return render(request, 'admin/admin_service_filter.html', {'data': data})


def create_paypal_payment(request, id):
    booking = Appointment.objects.get(id=id)

    # amount from booking
    amount = booking.worker.payment

    # Create payment record first
    payment = Payment.objects.create(
        user=booking.user_profile,
        booking=booking,
        worker=booking.worker,
        payment_method="paypal",
    )

    access_token = get_paypal_access_token()

    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    data = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": str(amount)
                }
            }
        ],
        "application_context": {
            "return_url": f"http://127.0.0.1:8000/payment-success/{payment.id}/",
            "cancel_url": f"http://127.0.0.1:8000/payment-cancel/{payment.id}/"
        }
    }

    response = requests.post(url, json=data, headers=headers)
    result = response.json()

    # Save order_id in DB
    payment.order_id = result.get("id")
    payment.save()

    # Mark appointment as pending payment
    booking.payment_status = 0
    booking.save()

    # redirect user to PayPal
    for link in result["links"]:
        if link["rel"] == "approve":
            return redirect(link["href"])

    return JsonResponse(result)


def payment_success(request, id):
    payment = Payment.objects.get(id=id)
    booking = payment.booking

    access_token = get_paypal_access_token()

    # Capture payment
    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders/{payment.order_id}/capture"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.post(url, headers=headers)
    result = response.json()

    # Check if payment success
    if result.get("status") == "COMPLETED":
        payment.payment_id = result["id"]
        payment.save()

        booking.payment_status = 1  # PAID
        booking.save()

        return redirect('user_view_appointment')

    booking.payment_status = 2  # FAILED
    booking.save()

    return redirect('user_view_appointment')


def payment_cancel(request, id):
    payment = Payment.objects.get(id=id)

    payment.booking.payment_status = 3
    payment.booking.save()

    return redirect('user_view_appointment')


def payment_details(request, id):
    data = Payment.objects.get(id=id)
    return render(request, 'user/payment.html', {'data': data})


def admin_payment_details(request, id):
    data = Payment.objects.get(id=id)
    return render(request, 'admin/admin_payment.html', {'data': data})


def worker_payment_details(request, id):
    data = Payment.objects.get(id=id)
    return render(request, 'worker/worker_payment.html', {'data': data})


def update_offline_payment(request, id):
    data = Appointment.objects.get(id=id)
    method = Payment.objects.get(id=id)
    data.payment_status = 1
    data.save()
    method.payment_method = "offline"
    method.save()
    return redirect('worker_view_appointment')


def create_worker_payout(request, id):
    booking = Appointment.objects.get(id=id)

    if not booking.worker_amount:
        return JsonResponse({"error": "Worker amount not set"}, status=400)

    if not booking.worker.paypal_email:
        return JsonResponse({"error": "Worker PayPal email missing"}, status=400)

    amount = f"{float(booking.worker_amount):.2f}"

    access_token = get_paypal_access_token()

    url = f"{settings.PAYPAL_BASE_URL}/v1/payments/payouts"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    data = {
        "sender_batch_header": {
            "sender_batch_id": str(uuid.uuid4()),
            "email_subject": "You have received a payment"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "receiver": booking.worker.paypal_email,
                "amount": {
                    "value": amount,
                    "currency": "USD"
                },
                "note": f"Payment for booking #{booking.id}",
                "sender_item_id": str(booking.id)
            }
        ]
    }

    response = requests.post(url, json=data, headers=headers)
    result = response.json()

    if result.get("name"):
        booking.worker_payment_status = 2  # FAILED
        booking.save()
        return JsonResponse(result, status=400)

    booking.worker_payment_status = 1  # PAID
    booking.save()

    return JsonResponse({
        "message": "Payment sent successfully",
        "payout_batch_id": result.get("batch_header", {}).get("payout_batch_id")
    })


def worker_wallet(request):
    worker = WorkerRegistration.objects.get(user=request.user)
    data = Appointment.objects.filter(worker=worker, worker_payment_status=1)
    total_earnings = sum(item.worker_amount or 0 for item in data)
    return render(request, 'worker/Wallet.html', {'data': data, 'total_earnings': total_earnings})


def completed_payment_details(request):
    data = Appointment.objects.filter(payment_status=1)
    total_earnings = 0
    total_admin_earnings = 0
    for item in data:
        payment_amount = item.worker.payment or 0
        admin_wallet = payment_amount * 0.20
        item.admin_wallet=admin_wallet
        item.save()
        total_earnings += payment_amount
        total_admin_earnings += admin_wallet
    context = {
        "data": data,
        "total_earnings": total_earnings,
        "total_admin_earnings": total_admin_earnings,
    }

    return render(request, 'admin/paymentDetails.html', context)
