# Generated by Django 5.1.7 on 2025-03-27 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_sale'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='cost_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
            preserve_default=False,
        ),
    ]
