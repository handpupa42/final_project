from decimal import Decimal
from django.contrib import messages
import csv
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from .forms import OrderCreateForm, ReviewForm, SellerProductForm
from .models import CartItem, Category, GiftCard, Order, OrderItem, Product


def is_seller_check(user):
    """Проверка прав: доступ в кабинет продавца только для персонала и администраторов."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def home(request):
    """Главная страница магазина с промо-блоком и новинками."""
    latest_products = Product.objects.filter(is_available=True)[:3]
    return render(
        request, "shop/home.html", {"latest_products": latest_products}
    )


def product_list(request, category_slug=None):
    """Каталог товаров с фильтрацией по категориям, поиском, диапазоном цен и сортировкой."""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
    query = request.GET.get("q")
    sort = request.GET.get("sort", "newest")
    in_stock = request.GET.get("in_stock")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(description__icontains=query)
            | Q(ingredients__icontains=query)
        )

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    if in_stock == "1":
        products = products.filter(stock__gt=0)

    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except Exception:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except Exception:
            pass

    # Сортировка
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "name":
        products = products.order_by("name")
    else:
        products = products.order_by("-created")

    return render(
        request,
        "shop/product_list.html",
        {
            "category": category,
            "categories": categories,
            "products": products,
            "query": query,
            "sort": sort,
            "in_stock": in_stock,
            "min_price": min_price,
            "max_price": max_price,
        },
    )


def product_detail(request, slug):
    """Детальная страница товара со списком отзывов и формой добавления нового отзыва."""
    product = get_object_or_404(Product, slug=slug, is_available=True)
    review_form = ReviewForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Ваш отзыв успешно опубликован!")
            return redirect("shop:product_detail", slug=slug)

    return render(
        request,
        "shop/product_detail.html",
        {"product": product, "review_form": review_form},
    )



@login_required
def cart_detail(request):
    """Просмотр корзины текущего пользователя с расчетом общей суммы."""
    cart_items = CartItem.objects.filter(user=request.user).select_related("product")
    total_cost = sum(item.get_total_price() for item in cart_items)
    return render(
        request,
        "shop/cart.html",
        {"cart_items": cart_items, "total_cost": total_cost},
    )


@login_required
def add_to_cart(request, product_id):
    """Добавление единицы товара в корзину с учетом складского остатка."""
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, product=product
    )
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Товар «{product.name}» добавлен в корзину.")
        else:
            messages.warning(request, f"На складе доступно всего {product.stock} шт.")
    else:
        messages.success(request, f"Товар «{product.name}» добавлен в корзину.")
    return redirect("shop:cart_detail")


@login_required
def remove_from_cart(request, item_id):
    """Удаление позиции из корзины."""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.info(request, "Товар удален из корзины.")
    return redirect("shop:cart_detail")




@login_required
def checkout(request):
    """Оформление заказа, списание подарочной карты, уменьшение остатков на складе."""
    cart_items = list(
        CartItem.objects.filter(user=request.user).select_related("product")
    )
    if not cart_items:
        return redirect("shop:cart_detail")

    subtotal = sum(
        (item.product.price * item.quantity for item in cart_items),
        Decimal("0.00"),
    )
    discount = Decimal("0.00")
    total_cost = subtotal

    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        card_code = request.POST.get("gift_card_code", "").strip().upper()
        gift_card = None

        if card_code:
            try:
                gift_card = GiftCard.objects.get(code=card_code)
                if gift_card.is_used:
                    form.add_error("gift_card_code", "Эта подарочная карта уже была использована ранее!")
                else:
                    discount = Decimal(str(gift_card.amount))
                    total_cost = max(Decimal("0.00"), subtotal - discount)
            except GiftCard.DoesNotExist:
                form.add_error("gift_card_code", "Подарочная карта с таким промокодом не найдена.")

        if form.is_valid():
            with transaction.atomic():

                for item in cart_items:
                    if not item.product.is_available or item.product.stock < item.quantity:
                        form.add_error(
                            None,
                            f"Недостаточно товара «{item.product.name}» на складе (осталось {item.product.stock} шт.).",
                        )
                        break

                if not form.errors:
                    order = form.save(commit=False)
                    order.user = request.user
                    order.discount = discount
                    order.total_cost = total_cost
                    if gift_card and not gift_card.is_used:
                        order.applied_gift_card = gift_card
                        gift_card.is_used = True
                        gift_card.save()
                    order.save()


                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            price=item.product.price,
                            quantity=item.quantity,
                        )
                        item.product.stock -= item.quantity
                        if item.product.stock == 0:
                            item.product.is_available = False
                        item.product.save(update_fields=["stock", "is_available"])

                    CartItem.objects.filter(user=request.user).delete()
                    return render(request, "shop/order_success.html", {"order": order})
    else:
        form = OrderCreateForm()

    return render(
        request,
        "shop/checkout.html",
        {
            "form": form,
            "cart_items": cart_items,
            "subtotal": subtotal,
            "total_cost": total_cost,
        },
    )

@login_required
def my_orders(request):
    """История покупок текущего пользователя со статусами."""
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    return render(request, "shop/my_orders.html", {"orders": orders})


@login_required
def order_track(request, order_id):
    """Интерактивный экран отслеживания конкретного заказа с шагами доставки."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    steps = ["created", "processing", "in_transit", "delivered"]
    current_step_index = steps.index(order.status) if order.status in steps else 0
    return render(
        request,
        "shop/order_track.html",
        {
            "order": order,
            "steps": steps,
            "current_step_index": current_step_index,
        },
    )


@login_required
def buy_gift_card(request):
    """Покупка цифровой карты выбранного номинала с генерацией уникального промокода."""
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


@login_required
def use_gift_card(request):
    """Проверка баланса и валидности промокода подарочной карты."""
    message = None
    success = False
    card = None
    if request.method == "POST":
        code = request.POST.get("code", "").strip().upper()
        try:
            card = GiftCard.objects.get(code=code)
            if card.is_used:
                message = "Данная карта уже была использована ранее!"
            else:
                success = True
                message = (
                    f"Карта активна! Её номинал: {card.amount} ₽. "
                    "Вы можете применить этот промокод на странице оформления заказа в корзине."
                )
        except GiftCard.DoesNotExist:
            message = "Подарочная карта с таким промокодом не найдена."

    return render(
        request,
        "shop/use_gift_card.html",
        {"message": message, "success": success, "card": card},
    )


@login_required
@user_passes_test(is_seller_check, login_url="shop:home")
def seller_dashboard(request):
    """Панель управления продавца: только его товары, статистика и заказы с его товарами."""
    my_products = Product.objects.filter(seller=request.user)
    seller_items = (
        OrderItem.objects.filter(product__seller=request.user)
        .select_related("order", "product")
        .order_by("-order__created_at")
    )

    total_earned = (
        sum(item.get_cost() for item in seller_items)
        if seller_items
        else Decimal("0.00")
    )
    total_units_sold = sum(item.quantity for item in seller_items)

    return render(
        request,
        "shop/seller_dashboard.html",
        {
            "my_products": my_products,
            "seller_items": seller_items,
            "total_earned": total_earned,
            "total_units_sold": total_units_sold,
        },
    )


@login_required
@user_passes_test(is_seller_check, login_url="shop:home")
def seller_add_product(request):
    """Добавление нового товара в продажу продавцом."""
    if request.method == "POST":
        form = SellerProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            base_slug = slugify(product.name) or "product"
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            product.slug = slug
            product.save()
            messages.success(request, f"Товар «{product.name}» успешно опубликован!")
            return redirect("shop:seller_dashboard")
    else:
        form = SellerProductForm()

    return render(request, "shop/seller_add_product.html", {"form": form})


@login_required
@user_passes_test(is_seller_check, login_url="shop:home")
def seller_update_status(request, order_id):
    """Смена статуса доставки заказа продавцом."""
    order = get_object_or_404(Order, id=order_id)
    has_seller_item = OrderItem.objects.filter(
        order=order, product__seller=request.user
    ).exists()

    if has_seller_item or request.user.is_superuser:
        if request.method == "POST":
            new_status = request.POST.get("status")
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save()
                messages.success(
                    request,
                    f"Статус заказа №{order.id} изменен на «{order.get_status_display()}».",
                )
    else:
        messages.error(request, "У вас нет прав для изменения этого заказа.")

    return redirect("shop:seller_dashboard")


def register(request):
    """Регистрация нового покупателя с автоматическим входом после создания."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}! Аккаунт успешно создан.")
            return redirect("shop:home")
    else:
        form = UserCreationForm()

    return render(request, "shop/register.html", {"form": form})

@login_required
def toggle_favorite(request, product_id):
    """Добавить или удалить товар из списка избранного."""
    product = get_object_or_404(Product, id=product_id)
    if request.user in product.favorites.all():
        product.favorites.remove(request.user)
        messages.info(request, f"Товар «{product.name}» удален из избранного.")
    else:
        product.favorites.add(request.user)
        messages.success(request, f"Товар «{product.name}» добавлен в избранное ❤️")
    
    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))


@login_required
def wishlist(request):
    """Просмотр отложенных товаров покупателя."""
    favorite_products = request.user.favorite_products.filter(is_available=True)
    return render(request, "shop/wishlist.html", {"products": favorite_products})


@login_required
@user_passes_test(is_seller_check, login_url="shop:home")
def seller_export_csv(request):
    """Экспорт отчета о продажах продавца в файл CSV (для Excel)."""
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID Заказа', 'Дата', 'Товар', 'Количество', 'Цена за ед. (руб)', 'Сумма (руб)', 'Статус', 'Покупатель'])

    seller_items = OrderItem.objects.filter(product__seller=request.user).select_related('order', 'product', 'order__user')

    for item in seller_items:
        writer.writerow([
            item.order.id,
            item.order.created_at.strftime('%d.%m.%Y %H:%M'),
            item.product.name if item.product else 'Товар удален',
            item.quantity,
            item.price,
            item.get_cost(),
            item.order.get_status_display(),
            item.order.user.username,
        ])

    return response

@login_required
def order_invoice(request, order_id):
    """Страница официального товарного чека заказа для печати/PDF."""
    order = get_object_or_404(Order, id=order_id)
    is_seller = OrderItem.objects.filter(order=order, product__seller=request.user).exists()
    if order.user != request.user and not is_seller and not request.user.is_superuser:
        messages.error(request, "У вас нет доступа к этому чеку.")
        return redirect("shop:home")

    return render(request, "shop/order_invoice.html", {"order": order})