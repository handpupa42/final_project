from decimal import Decimal
import uuid
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
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
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_products', verbose_name="Продавец", null=True, blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название товара")
    slug = models.SlugField(max_length=200, unique=True)
    brand = models.CharField(max_length=100, verbose_name="Бренд")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Фото товара")
    description = models.TextField(verbose_name="Описание")
    ingredients = models.TextField(verbose_name="Состав", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена (₽)")
    stock = models.PositiveIntegerField(default=10, verbose_name="В наличии")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    created = models.DateTimeField(auto_now_add=True)
    
    favorites = models.ManyToManyField(User, related_name='favorite_products', blank=True, verbose_name="В избранном у")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ('-created',)

    def __str__(self):
        return f"{self.brand} — {self.name}"

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

    @property
    def average_rating(self):
        ratings = self.reviews.all()
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 1)
        return None



class Review(models.Model):
  product = models.ForeignKey(
      Product,
      on_delete=models.CASCADE,
      related_name="reviews",
      verbose_name="Товар",
  )
  user = models.ForeignKey(
      User, on_delete=models.CASCADE, verbose_name="Автор"
  )
  rating = models.PositiveSmallIntegerField(
      validators=[MinValueValidator(1), MaxValueValidator(5)],
      verbose_name="Оценка (1-5)",
  )
  text = models.TextField(verbose_name="Отзыв")
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    verbose_name = "Отзыв"
    verbose_name_plural = "Отзывы"
    ordering = ("-created_at",)


class CartItem(models.Model):
  user = models.ForeignKey(
      User, on_delete=models.CASCADE, related_name="cart"
  )
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(default=1)

  def get_total_price(self):
    return self.product.price * self.quantity


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
  is_used = models.BooleanField(default=False, verbose_name="Использована")
  created_at = models.DateTimeField(auto_now_add=True)

  def save(self, *args, **kwargs):
    if not self.code:
      self.code = f"GB-{uuid.uuid4().hex[:8].upper()}"
    super().save(*args, **kwargs)

  class Meta:
    verbose_name = "Подарочная карта"
    verbose_name_plural = "Подарочные карты"

  def __str__(self):
    return f"{self.code} ({self.amount} ₽) — {'Использована' if self.is_used else 'Активна'}"


class Order(models.Model):
  STATUS_CHOICES = [
      ("created", "Оформлен"),
      ("processing", "Собирается"),
      ("in_transit", "В пути к получателю"),
      ("delivered", "Доставлен"),
      ("canceled", "Отменён"),
  ]

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
  discount = models.DecimalField(
      max_digits=10,
      decimal_places=2,
      default=Decimal("0.00"),
      verbose_name="Скидка по сертификату",
  )
  total_cost = models.DecimalField(
      max_digits=10, decimal_places=2, verbose_name="Итоговая сумма"
  )
  status = models.CharField(
      max_length=20,
      choices=STATUS_CHOICES,
      default="created",
      verbose_name="Статус",
  )
  applied_gift_card = models.ForeignKey(
      GiftCard,
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      verbose_name="Использованная карта",
  )

  class Meta:
    verbose_name = "Заказ"
    verbose_name_plural = "Заказы"
    ordering = ("-created_at",)

  def __str__(self):
    return f"Заказ №{self.id} [{self.get_status_display()}] — {self.user.username}"


class OrderItem(models.Model):
  order = models.ForeignKey(
      Order,
      related_name="items",
      on_delete=models.CASCADE,
      verbose_name="Заказ",
  )
  product = models.ForeignKey(
      Product,
      on_delete=models.SET_NULL,
      null=True,
      verbose_name="Товар",
  )
  price = models.DecimalField(
      max_digits=10, decimal_places=2, verbose_name="Цена при покупке"
  )
  quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

  def get_cost(self):
    return self.price * self.quantity

  def __str__(self):
    return f"{self.product.name if self.product else 'Товар удален'} ({self.quantity} шт.)"