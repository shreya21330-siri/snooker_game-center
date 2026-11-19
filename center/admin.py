
from django.contrib import admin
from .models import (
    EmployeeProfile,
    Customer,
    GamingTable,
    Booking,
    Payment,
    MembershipPlan,
    CustomerMembership,
    Tournament,
)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('created_at',)


@admin.register(GamingTable)
class GamingTableAdmin(admin.ModelAdmin):
    list_display = (
        'table_number',
        'table_type',
        'hourly_rate',
        'status',
    )
    list_filter = ('table_type', 'status')
    search_fields = ('table_number',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'gaming_table',
        'booking_date',
        'expected_end_time',
        'status',
        'hourly_rate',
    )
    list_filter = ('status', 'booking_date')
    search_fields = (
        'customer__name',
        'gaming_table__table_number',
    )
    readonly_fields = ('created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'booking',
        'amount',
        'payment_method',
        'status',
        'paid_at',
    )
    list_filter = ('payment_method', 'status')
    search_fields = (
        'transaction_reference',
        'booking__customer__name',
    )


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(CustomerMembership)
class CustomerMembershipAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'plan',
        'start_date',
        'end_date',
        'status',
    )
    list_filter = ('status', 'start_date')
    search_fields = ('customer__name', 'plan__name')


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'game_type',
        'start_date',
        'end_date',
        'entry_fee',
        'status',
    )
    list_filter = ('game_type', 'status')
    search_fields = ('name',)


# Register your models here.
