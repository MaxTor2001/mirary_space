"""Толщина, длина и тип резьбы вместо прежнего текстового размера."""
import re
from decimal import Decimal

import django.contrib.postgres.fields
from django.db import migrations, models


def split_size(apps, schema_editor):
    """Разносит прежний размер «1.2x8 мм» по толщине и длине."""
    Product = apps.get_model("goods", "Product")
    for product in Product.objects.exclude(size=""):
        numbers = [Decimal(n) for n in re.findall(r"\d+(?:\.\d+)?", product.size.replace(",", "."))]
        if len(numbers) == 2:
            product.thicknesses, product.lengths = numbers[:1], numbers[1:]
        elif len(numbers) == 1:
            product.lengths = numbers
        else:
            continue
        product.save(update_fields=["thicknesses", "lengths"])


class Migration(migrations.Migration):

    dependencies = [
        ("goods", "0003_alter_product_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="thicknesses",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.DecimalField(decimal_places=1, max_digits=4),
                blank=True, default=list, verbose_name="Толщина, мм",
                help_text="Несколько значений — через запятую: 1.2, 1.6",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="lengths",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.DecimalField(decimal_places=1, max_digits=4),
                blank=True, default=list, verbose_name="Длина, мм",
                help_text="Несколько значений — через запятую: 6, 8, 10",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="thread",
            field=models.CharField(
                blank=True, max_length=20, verbose_name="Тип резьбы",
                choices=[
                    ("internal", "Внутренняя резьба"),
                    ("external", "Внешняя резьба"),
                    ("threadless", "Безрезьбовое (push-in)"),
                ],
            ),
        ),
        migrations.RunPython(split_size, migrations.RunPython.noop),
        migrations.RemoveField(model_name="product", name="size"),
    ]
