
from django.db import models
from django.contrib.auth.models import User


# 1. OWNER AND RECEPTIONIST
class EmployeeProfile(models.Model):

    ROLE_CHOICES = [
        ('OWNER', 'Owner'),
        ('RECEPTIONIST', 'Receptionist'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# 2. CUSTOMERS
class Customer(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_profile'
    )

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 3. SNOOKER AND POOL TABLES
class GamingTable(models.Model):

    TABLE_TYPES = [
        ('SNOOKER', 'Snooker'),
        ('POOL', 'Pool'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('MAINTENANCE', 'Maintenance'),
    ]

    table_number = models.CharField(max_length=20)
    table_type = models.CharField(
        max_length=20,
        choices=TABLE_TYPES
    )

    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['table_number', 'table_type'],
                name='unique_gaming_table_number_type'
            )
        ]

    def __str__(self):
        return f"{self.table_type} - {self.table_number}"


# 4. BOOKINGS
class Booking(models.Model):

    STATUS_CHOICES = [
        ('BOOKED', 'Booked'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT
    )

    gaming_table = models.ForeignKey(
        GamingTable,
        on_delete=models.PROTECT
    )

    receptionist = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    booking_date = models.DateTimeField()
    expected_end_time = models.DateTimeField()

    actual_start_time = models.DateTimeField(
        null=True,
        blank=True
    )

    actual_end_time = models.DateTimeField(
        null=True,
        blank=True
    )

    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='BOOKED'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - {self.customer.name}"


# 5. PAYMENTS
class Payment(models.Model):

    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
        ('CARD', 'Card'),
    ]

    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('REFUNDED', 'Refunded'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='PENDING'
    )

    transaction_reference = models.CharField(
        max_length=100,
        blank=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Payment {self.id} - {self.amount}"


# 6. MEMBERSHIP PLANS
class MembershipPlan(models.Model):

    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    duration_days = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# 7. CUSTOMER MEMBERSHIPS
class CustomerMembership(models.Model):

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT
    )

    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.PROTECT
    )

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    def __str__(self):
        return f"{self.customer.name} - {self.plan.name}"


# 8. TOURNAMENTS
class Tournament(models.Model):

    GAME_TYPES = [
        ('SNOOKER', 'Snooker'),
        ('POOL', 'Pool'),
    ]

    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    name = models.CharField(max_length=150)

    game_type = models.CharField(
        max_length=20,
        choices=GAME_TYPES
    )

    start_date = models.DateField()
    end_date = models.DateField()

    entry_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    participants = models.ManyToManyField(
        Customer,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='UPCOMING'
    )

    def __str__(self):
        return self.name

# Create your models here.
