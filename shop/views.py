from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import CartItem, Category, GiftCard, Product


def home(request):
  latest_products = Product.objects.filter(is_available=True)[:3]
  return render(
      request, "shop/home.html", {"latest_products": latest_products}
  )


def product_list(request, category_slug=None):
  category = None
  categories = Category.objects.all()
  products = Product.objects.filter(is_available=True)
  query = request.GET.get("q")

  if query:
    products = products.filter(
        Q(name__icontains=query) | Q(brand__icontains=query)
    )

  if category_slug:
    category = get_object_or_404(Category, slug=category_slug)
    products = products.filter(category=category)

  return render(
      request,
      "shop/product_list.html",
      {"category": category, "categories": categories, "products": products},
  )


def product_detail(request, slug):
  product = get_object_or_404(Product, slug=slug, is_available=True)
  return render(request, "shop/product_detail.html", {"product": product})


@login_required
def cart_detail(request):
  cart_items = CartItem.objects.filter(user=request.user).select_related(
      "product"
  )
  total_cost = sum(item.get_total_price() for item in cart_items)
  return render(
      request,
      "shop/cart.html",
      {"cart_items": cart_items, "total_cost": total_cost},
  )


@login_required
def add_to_cart(request, product_id):
  product = get_object_or_404(Product, id=product_id)
  cart_item, created = CartItem.objects.get_or_create(
      user=request.user, product=product
  )
  if not created:
    cart_item.quantity += 1
    cart_item.save()
  return redirect("shop:cart_detail")


@login_required
def remove_from_cart(request, item_id):
  cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
  cart_item.delete()
  return redirect("shop:cart_detail")


@login_required
def checkout(request):
  cart_items = CartItem.objects.filter(user=request.user)
  total_cost = sum(item.get_total_price() for item in cart_items)
  return render(
      request,
      "shop/checkout.html",
      {"cart_items": cart_items, "total_cost": total_cost},
  )


@login_required
def buy_gift_card(request):
  if request.method == "POST":
    amount = request.POST.get("amount")
    email = request.POST.get("email")
    message = request.POST.get("message")

    card = GiftCard.objects.create(
        buyer=request.user,
        amount=amount,
        recipient_email=email,
        message=message,
    )
    return render(request, "shop/gift_card_success.html", {"card": card})

  return render(
      request,
      "shop/buy_gift_card.html",
      {"amounts": GiftCard.VALUE_CHOICES},
  )


def register(request):
  if request.method == "POST":
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect("shop:home")
  else:
    form = UserCreationForm()
  return render(request, "shop/register.html", {"form": form})
