# Generated by Django 4.2.7 on 2023-12-28 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0033_product_supercategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='superCategory',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
