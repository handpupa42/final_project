from django.contrib import admin
from .models import CartItem, Category, GiftCard, Order, OrderItem, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'slug')
  prepopulated_fields = {'slug': ('name',)}
  search_fields = ('name',)


class OrderItemInline(admin.TabularInline):
  model = OrderItem
  extra = 0
  readonly_fields = ('product', 'price', 'quantity')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = (
      'brand',
      'name',
      'seller',
      'category',
      'price',
      'stock',
      'is_available',
  )
  list_filter = ('is_available', 'category', 'brand')
  list_editable = ('price', 'stock', 'is_available')
  search_fields = ('name', 'brand', 'description')
  prepopulated_fields = {'slug': ('name',)}
  autocomplete_fields = ('category', 'seller')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  list_display = (
      'id',
      'user',
      'phone',
      'total_cost',
      'discount',
      'status',
      'created_at',
  )
  list_filter = ('status', 'created_at')
  list_editable = ('status',)
  search_fields = ('first_name', 'last_name', 'phone', 'address')
  inlines = [OrderItemInline]


@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
  list_display = (
      'code',
      'buyer',
      'amount',
      'recipient_email',
      'is_used',
      'created_at',
  )
  list_filter = ('is_used', 'amount', 'created_at')
  search_fields = ('code', 'recipient_email')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
  list_display = ('product', 'user', 'rating', 'created_at')
  list_filter = ('rating', 'created_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
  list_display = ('user', 'product', 'quantity')
