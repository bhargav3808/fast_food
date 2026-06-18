from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem, DeliveryAddress, DeliveryPerson, Delivery

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'active', 'created_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'status', 'delivery_address', 'created_at')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'total', 'status', 'created_at')
        }),
        ('Delivery', {
            'fields': ('delivery_address', 'cart')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'subtotal')

@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street_address', 'city', 'is_default')
    list_filter = ('is_default', 'city')
    search_fields = ('user__username', 'street_address', 'city')
    fieldsets = (
        ('Address Information', {
            'fields': ('user', 'street_address', 'city', 'postal_code', 'phone')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_default',)
        }),
    )

@admin.register(DeliveryPerson)
class DeliveryPersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'status', 'total_deliveries')
    list_filter = ('status', 'total_deliveries')
    search_fields = ('user__username', 'phone', 'vehicle_info')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone')
        }),
        ('Vehicle & Status', {
            'fields': ('vehicle_info', 'status')
        }),
        ('Location Tracking', {
            'fields': ('current_latitude', 'current_longitude'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_deliveries',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivery_person', 'status', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__id', 'delivery_person__user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Order & Assignment', {
            'fields': ('order', 'delivery_person')
        }),
        ('Status Information', {
            'fields': ('status', 'estimated_delivery_time', 'actual_delivery_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_assigned', 'mark_as_in_transit', 'mark_as_delivered']

    def mark_as_assigned(self, request, queryset):
        updated = queryset.update(status='assigned')
        self.message_user(request, f'{updated} deliveries marked as assigned.')
    mark_as_assigned.short_description = 'Mark selected as assigned'

    def mark_as_in_transit(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='in_transit')
        self.message_user(request, f'{queryset.count()} deliveries marked as in transit.')
    mark_as_in_transit.short_description = 'Mark selected as in transit'

    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='delivered', actual_delivery_time=timezone.now())
        self.message_user(request, f'{queryset.count()} deliveries marked as delivered.')
    mark_as_delivered.short_description = 'Mark selected as delivered'
