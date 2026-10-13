🖤 Glow & Beauty — Dark Edition (Дипломный проект)
интернет-магазин уходовой и декоративной косметики на Python и Django 5 с системой подарочных карт.
Основные возможности
Главная страница (Landing): Блок-баннер, преимущества бренда, новинки.
Каталог товаров (/products/): Сетка товаров с фотографиями, ценами, брендами и фильтрацией по категориям.
Карточка товара: Подробная страница с фото, наличием на складе, описанием и составом (INCI).
Подарочные карты (/gift-card/): Покупка виртуальных сертификатов выбранного номинала (1 000 ₽, 3 000 ₽, 5 000 ₽, 10 000 ₽) с автоматической генерацией уникального 12-значного промокода и отправкой на email получателя.
Корзина и заказы: Персональная корзина покупок, оформление заказов с сохранением контактных данных в БД.
Авторизация и профили: Регистрация, вход/выход, защита оформления заказа и покупки подарочных карт авторизацией.
Панель администратора: Управление категориями, товарами, заказами и активированными подарочными картами.
Технологический стек
Язык: Python 3.10+
Фреймворк: Django 5.x
База данных: SQLite3
Обработка изображений: Pillow
Фронтенд: HTML5, CSS3 (Dark Theme), Bootstrap 5, Google Fonts (Outfit, Plus Jakarta Sans)
 Инструкция по установке и запуску
1. Переход в папку проекта
Откройте терминал (PowerShell или CMD) в папке проекта, где находится файл manage.py:
# Проверка текущего содержимого
dir
2. Виртуальное окружение
# Создание окружения
python -m venv venv

# Активация на Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Активация на Windows (CMD)
venv\Scripts\activate.bat

# Активация на Mac / Linux
source venv/bin/activate
3. Установка зависимостей
pip install -r requirements.txt
(Или вручную: pip install Django Pillow).
4. Применение миграций базы данных
python manage.py makemigrations shop
python manage.py migrate
5. Создание администратора
python manage.py createsuperuser
6. Запуск сервера
python manage.py runserver
Страницы в браузере:
Главная страница: http://127.0.0.1:8000/
Каталог товаров: http://127.0.0.1:8000/products/
Подарочные карты: http://127.0.0.1:8000/gift-card/
Админка: http://127.0.0.1:8000/admin/
Карта маршрутов (URL Structure)
URL	Имя (Name)	Описание
/	shop:home	Главная страница
/products/	shop:product_list	Полный каталог косметики
/category/<slug>/	shop:product_list_by_category	Фильтр по категориям
/product/<slug>/	shop:product_detail	Детальная страница товара
/gift-card/	shop:buy_gift_card	Форма покупки подарочной карты
/cart/	shop:cart_detail	Корзина покупателя
/cart/add/<id>/	shop:add_to_cart	Добавление товара в корзину
/cart/remove/<id>/	shop:remove_from_cart	Удаление товара из корзины
/checkout/	shop:checkout	Оформление заказа
/login/	login	Авторизация
/register/	shop:register	Регистрация нового покупателя
/admin/	—	Панель управления магазином(логин:admin, пароль:admin1)
❓ Частые вопросы и их решение
Ошибка TemplateDoesNotExist: Убедитесь, что все HTML-шаблоны находятся в папке templates/shop/, а главный шаблон base.html — прямо в templates/base.html.
При миграциях спрашивает default value (timezone.now): Введите 1, затем нажмите Enter — Django подставит текущую дату и время для существующих записей.
Не загружаются картинки: Убедитесь, что установлена библиотека Pillow и в config/urls.py прописан раздачик settings.MEDIA_URL.
Glow & Beauty — Dark Edition 2026.