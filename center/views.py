from datetime import datetime

from django.shortcuts import render, redirect
from django.utils import timezone

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