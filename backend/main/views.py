"""API главной страницы, контактов и информационных разделов."""
import os

from rest_framework.decorators import api_view
from rest_framework.response import Response

from goods.models import Category, Product
from goods.serializers import CategorySerializer, ProductSerializer

from .models import Banner
from .serializers import BannerSerializer

REQUISITES = {
    "legal_name": os.environ.get("SHOP_LEGAL_NAME", "ИП Канищева Екатерина Владимировна"),
    "inn": os.environ.get("SHOP_INN", "745110010453"),
}

CONTACTS = {
    "shop": "Mirari",
    "tagline": "Украшения для пирсинга из титана и стали",
    "phone": "+7 (999) 123-45-67",
    "email": "hello@mirari.shop",
    "address": "Москва, ул. Пирсинговая, 7",
    "work_hours": "Ежедневно с 10:00 до 21:00",
    "requisites": REQUISITES,
}

ABOUT = {
    "story": {
        "title": "О нас",
        "text": (
            "Mirari — интернет-магазин украшений для пирсинга: титан G23, хирургическая "
            "сталь 316L и расходники для мастеров."
        ),
    },
    "advantages": [
        {
            "title": "Сертифицированные материалы",
            "description": "Только титан G23, хирургическая сталь 316L и золото высокого качества",
        },
        {
            "title": "Профессиональные мастера",
            "description": "Консультация и помощь в выборе украшений",
        },
        {"title": "Быстрая доставка", "description": "По России за 1–3 дня"},
        {"title": "Гарантия качества", "description": "Возврат в течение 14 дней"},
    ],
    "requisites": REQUISITES,
}

DELIVERY = {
    "shipping": [
        {
            "title": "Курьерская доставка",
            "terms": "По Москве и Санкт-Петербургу — 1–2 дня",
            "price": "от 300 ₽, бесплатно при заказе от 5 000 ₽",
        },
        {
            "title": "Пункты выдачи и постаматы",
            "terms": "СДЭК, Boxberry — по всей России, 2–7 дней",
            "price": "от 200 ₽",
        },
        {
            "title": "Почта России",
            "terms": "Доставка в любой населённый пункт — 5–14 дней",
            "price": "от 250 ₽",
        },
        {
            "title": "Самовывоз",
            "terms": "Из пункта выдачи после оформления заказа",
            "price": "Бесплатно",
        },
    ],
    "payment": [
        "Банковской картой онлайн на сайте",
        "Через Систему быстрых платежей (СБП)",
        "Наличными или картой курьеру при получении",
        "На кассе пункта выдачи",
    ],
    "returns": (
        "Вы можете вернуть или обменять товар в течение 14 дней с момента получения, если он "
        "не был в использовании и сохранены товарный вид и упаковка."
    ),
}


@api_view(["GET"])
def home(request):
    """Данные главной: баннеры, категории и новинки каталога."""
    novelties = Product.objects.select_related("category").order_by("-created_at")[:8]
    return Response(
        {
            "banners": BannerSerializer(Banner.objects.filter(is_active=True), many=True).data,
            "categories": CategorySerializer(Category.objects.all(), many=True).data,
            "novelties": ProductSerializer(novelties, many=True).data,
        }
    )


@api_view(["GET"])
def contacts(request):
    return Response(CONTACTS)


@api_view(["GET"])
def about(request):
    """Раздел «О магазине»: история, преимущества и реквизиты."""
    return Response(ABOUT)


@api_view(["GET"])
def delivery(request):
    """Раздел «Доставка и оплата»."""
    return Response(DELIVERY)
