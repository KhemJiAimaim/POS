# Generated by Django 4.1.3 on 2023-02-01 20:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_orderitem_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('created',), 'verbose_name': 'การซื้อสินค้า', 'verbose_name_plural': 'ข้อมูลการซื้อสินค้า'},
        ),
        migrations.AlterModelOptions(
            name='orderitem',
            options={'ordering': ('created',), 'verbose_name': 'รายการสินค้าที่ขาย', 'verbose_name_plural': 'ข้อมูลรายการสินค้าที่ขาย'},
        ),
        migrations.AddField(
            model_name='product',
            name='EXP',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]