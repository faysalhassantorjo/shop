# Generated by Django 4.2.5 on 2023-09-13 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_product_discount_product_discount_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='hero_slide',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
