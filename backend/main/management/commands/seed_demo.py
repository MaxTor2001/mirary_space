"""Наполняет базу демонстрационным каталогом магазина Mirari."""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from goods.models import Category, Product
from main.models import Banner

CATEGORIES = [
    ("Серьги для носа", "nose", "Нострилы, септумы и кольца для носа"),
    ("Украшения для ушей", "ears", "Лабреты, туннели, хеликсы и индастриалы"),
    ("Пирсинг губ и языка", "lips", "Штанги и лабреты для губ и языка"),
    ("Пирсинг тела", "body", "Украшения для пупка, брови и микродермалов"),
    ("Инструменты и уход", "care", "Иглы, зажимы и антисептики для мастеров"),
]

# название, категория, материал, толщины, длины, резьба, цена, скидка, остаток
PRODUCTS = [
    ("Титановый лабрет Mirari Classic", "ears", "Титан G23", [1.2], [6, 8, 10], "internal", 1490, 10, 24),
    ("Кольцо-кликер для септума", "nose", "Хирургическая сталь 316L", [1.2], [8, 10], "threadless", 1290, 0, 30),
    ("Нострила с кристаллом Swarovski", "nose", "Титан G23", [0.8, 1.0], [6.5], "threadless", 1890, 15, 12),
    ("Штанга для языка с шариками", "lips", "Хирургическая сталь 316L", [1.6], [14, 16, 18], "external", 990, 0, 40),
    ("Лабрет для губы с опалом", "lips", "Титан G23", [1.2], [8, 10], "internal", 2190, 10, 8),
    ("Банан для пупка с подвеской", "body", "Хирургическая сталь 316L", [1.6], [10, 12], "external", 1590, 0, 18),
    ("Микродермал титановый", "body", "Титан G23", [1.2], [2.5], "internal", 890, 0, 50),
    ("Индастриал-штанга", "ears", "Титан G23", [1.6], [35, 38], "external", 2490, 20, 6),
    ("Туннель из акрила, пара", "ears", "Акрил", [], [8, 10, 12], "", 690, 0, 35),
    ("Игла-катетер для пирсинга, 10 шт", "care", "Сталь", [1.2, 1.6], [], "", 1190, 0, 25),
    ("Зажим Пеннингтона", "care", "Сталь", [], [], "", 2890, 5, 7),
    ("Антисептик Miramistin 150 мл", "care", "—", [], [], "", 590, 0, 60),
]


class Command(BaseCommand):
    help = "Создаёт демо-каталог, баннеры и администратора"

    def handle(self, *args, **options):
        categories = {}
        for name, slug, description in CATEGORIES:
            category, _ = Category.objects.update_or_create(
                slug=slug, defaults={"name": name, "description": description}
            )
            categories[slug] = category

        for name, cat_slug, material, thicknesses, lengths, thread, price, discount, quantity in PRODUCTS:
            slug = f"{cat_slug}-{name.lower().replace(' ', '-')[:40]}"
            Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": categories[cat_slug],
                    "material": material,
                    "thicknesses": thicknesses,
                    "lengths": lengths,
                    "thread": thread,
                    "price": price,
                    "discount": discount,
                    "quantity": quantity,
                    "description": f"{name}. Материал: {material}. "
                    "Гипоаллергенно, подходит для свежих проколов.",
                },
            )

        Banner.objects.update_or_create(
            title="Титан для свежих проколов",
            defaults={
                "subtitle": "Гипоаллергенные украшения Mirari — от прокола до заживления",
                "link": "/catalog/nose",
                "sort": 1,
            },
        )
        Banner.objects.update_or_create(
            title="Скидка 20% на индастриалы",
            defaults={"subtitle": "Только до конца месяца", "link": "/catalog/ears", "sort": 2},
        )

        user_model = get_user_model()
        if not user_model.objects.filter(username="admin").exists():
            password = os.environ.get("DJANGO_ADMIN_PASSWORD", "admin")
            user_model.objects.create_superuser("admin", "admin@mirari.shop", password)
            self.stdout.write("Создан администратор admin")

        self.stdout.write(self.style.SUCCESS("Демо-данные Mirari загружены"))
