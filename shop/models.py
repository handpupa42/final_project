import uuid
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Category(models.Model):
  name = models.CharField(max_length=100, verbose_name="Категория")
  slug = models.SlugField(max_length=100, unique=True)

  class Meta:
    verbose_name = "Категория"
    verbose_name_plural = "Категории"

  def __str__(self):
    return self.name


class Product(models.Model):
  category = models.ForeignKey(
      Category,
      related_name="products",
      on_delete=models.CASCADE,
      verbose_name="Категория",
  )
  name = models.CharField(max_length=200, verbose_name="Название товара")
  slug = models.SlugField(max_length=200, unique=True)
  brand = models.CharField(max_length=100, verbose_name="Бренд")
  image = models.ImageField(
    upload_to="products/", blank=True, null=True, verbose_name="Фото товара"
  )

  description = models.TextField(verbose_name="Описание")
  ingredients = models.TextField(verbose_name="Состав", blank=True)
  price = models.DecimalField(
      max_digits=10, decimal_places=2, verbose_name="Цена"
  )
  stock = models.PositiveIntegerField(default=10, verbose_name="В наличии")
  is_available = models.BooleanField(default=True, verbose_name="Доступен")
  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    verbose_name = "Товар"
    verbose_name_plural = "Товары"
    ordering = ("-created",)

  def __str__(self):
    return self.name

  def get_absolute_url(self):
    return reverse("shop:product_detail", args=[self.slug])


class CartItem(models.Model):
  user = models.ForeignKey(
      User, on_delete
=models.CASCADE, related_name="cart"
  )
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(default=1)

  def get_total_price(self):
    return self.product.price * self.quantity


class Order(models.Model):
  user = models.ForeignKey(
      User,
      on_delete=models.CASCADE,
      related_name="orders",
      verbose_name="Покупатель",
  )
  first_name = models.CharField(max_length=50, verbose_name="Имя")
  last_name = models.CharField(max_length=50, verbose_name="Фамилия")
  phone = models.CharField(max_length=20, verbose_name="Телефон")
  address = models.CharField(max_length=250, verbose_name="Адрес доставки")
  created_at = models.DateTimeField(
      auto_now_add=True, verbose_name="Дата заказа"
  )
  total_cost = models.DecimalField(
      max_digits=10, decimal_places=2, verbose_name="Сумма заказа"
  )
  is_paid = models.BooleanField(default=False, verbose_name="Оплачено")

  class Meta:
    verbose_name = "Заказ"
    verbose_name_plural = "Заказы"
    ordering = ("-created_at",)

  def __str__(self):
    return f"Заказ №{self.id} — {self.user.username}"


class GiftCard(models.Model):
  VALUE_CHOICES = [
      (1000, "1 000 ₽"),
      (3000, "3 000 ₽"),
      (5000, "5 000 ₽"),
      (10000, "10 000 ₽"),
  ]

  buyer = models.ForeignKey(
      User, on_delete=models.CASCADE, related_name="purchased_cards"
  )
  code = models.CharField(max_length=20, unique=True, editable=False)
  amount = models.PositiveIntegerField(
      choices=VALUE_CHOICES, verbose_name="Номинал"
  )
  recipient_email = models.EmailField(verbose_name="Email получателя")
  message = models.TextField(verbose_name="Поздравление", blank=True)
  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def save(self, *args, **kwargs):
    if not self.code:
      self.code = str(uuid.uuid4()).upper()[:12]
    super().save(*args, **kwargs)

  class Meta:
    verbose_name = "Подарочная карта"
    verbose_name_plural = "Подарочные карты"

  def __str__(self):
    return f"Карта на {self.amount} ₽ ({self.code})"