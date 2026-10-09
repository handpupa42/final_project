from django.contrib import admin
from .models import CartItem, Category, Order, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'slug')
  prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = (
      'brand',
      'name',
      'category',
      'price',
      'stock',
      'is_available',
      'created_at',
  )
  list_filter = ('is_available', 'category', 'brand')
  list_editable = ('price', 'stock', 'is_available')
  search_fields = ('name', 'brand', 'description')
  prepopulated_fields = {'slug': ('name',)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  list_display = (
      'id',
      'user',
      'first_name',
      'last_name',
      'phone',
      'total_cost',
      'is_paid',
      'created_at',
  )
  list_filter = ('is_paid', 'created_at')
  search_fields = ('first_name', 'last_name', 'phone', 'address')