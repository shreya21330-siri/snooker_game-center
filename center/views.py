
from datetime import datetime

from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

from .forms import CustomerRegistrationForm
from .models import Customer, GamingTable, Booking
from .email_utils import send_notification_email


def home(request):
    return render(request, 'home.html')


def create_booking(request):

    gaming_tables = GamingTable.objects.filter(status='ACTIVE')

    if request.method == 'POST':

        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        customer_email = request.POST.get('customer_email')
        table_id = request.POST.get('gaming_table')
        booking_date = request.POST.get('booking_date')
        expected_end_time = request.POST.get('expected_end_time')
        notes = request.POST.get('notes', '')

        try:
            table = GamingTable.objects.get(
                id=table_id,
                status='ACTIVE'
            )

            start_time = datetime.fromisoformat(booking_date)
            end_time = datetime.fromisoformat(expected_end_time)

            if timezone.is_naive(start_time):
                start_time = timezone.make_aware(start_time)

            if timezone.is_naive(end_time):
                end_time = timezone.make_aware(end_time)

            if end_time <= start_time:
                raise ValueError("End time must be after start time.")

            # Check whether this table is already booked
            overlapping_booking = Booking.objects.filter(
                gaming_table=table,
                status__in=['BOOKED', 'ONGOING'],
                booking_date__lt=end_time,
                expected_end_time__gt=start_time
            ).exists()

            if overlapping_booking:
                raise ValueError(
                    "This table is already booked for that time."
                )

            # Find existing customer or create a new one
            customer = Customer.objects.filter(
                phone=customer_phone
            ).first()

            if customer:
                customer.name = customer_name
                customer.email = customer_email
                customer.save()
            else:
                customer = Customer.objects.create(
                    name=customer_name,
                    phone=customer_phone,
                    email=customer_email
                )

            # Create booking
            booking = Booking.objects.create(
                customer=customer,
                gaming_table=table,
                receptionist=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),
                booking_date=start_time,
                expected_end_time=end_time,
                hourly_rate=table.hourly_rate,
                notes=notes
            )

            # Prepare email recipients
            recipients = [
                customer.email,
            ]

            if request.user.is_authenticated and request.user.email:
                recipients.append(request.user.email)

            from django.conf import settings

            if settings.OWNER_EMAIL:
                recipients.append(settings.OWNER_EMAIL)

            # Send demo notification
            try:
                send_notification_email(
                    "New Booking - BreakPoint Gaming",
                    f"""
Hello!

A new gaming booking has been created.

Booking ID: {booking.id}
Customer: {customer.name}
Phone: {customer.phone}
Game: {table.table_type}
Table: {table.table_number}
Start: {start_time}
End: {end_time}
Hourly Rate: Rs. {table.hourly_rate}

Thank you,
BreakPoint Gaming Center
""",
                    recipients
                )
            except Exception as email_error:
                print("Email notification error:", email_error)

            return render(
                request,
                'booking.html',
                {
                    'gaming_tables': gaming_tables,
                    'success': True,
                    'booking': booking
                }
            )

        except (GamingTable.DoesNotExist, ValueError, TypeError) as error:

            return render(
                request,
                'booking.html',
                {
                    'gaming_tables': gaming_tables,
                    'error': str(error)
                }
            )

    return render(
        request,
        'booking.html',
        {'gaming_tables': gaming_tables}
    )

def register_customer(request):

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            Customer.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email']
            )

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            verification_link = request.build_absolute_uri(
                reverse(
                    'verify_email',
                    kwargs={'uidb64': uid, 'token': token}
                )
            )

            send_mail(
                'Verify Your BreakPoint Account',
                f'Hello {user.first_name},\n\n'
                f'Click this link to verify your account:\n'
                f'{verification_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )

            return render(
                request,
                'accounts/register.html',
                {
                    'form': CustomerRegistrationForm(),
                    'message': 'Registration successful! Check your email to verify your account.'
                }
            )

    else:
        form = CustomerRegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )
def verify_email(request, uidb64, token):

    from django.utils.http import urlsafe_base64_decode

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):

        user.is_active = True
        user.save()

        login(request, user)

        return render(
            request,
            'accounts/email_verified.html'
        )

    return render(
        request,
        'accounts/invalid_link.html'
    )
def customer_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            return render(
                request,
                'accounts/login.html',
                {'error': 'Invalid username or password.'}
            )

    return render(request, 'accounts/login.html')
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')