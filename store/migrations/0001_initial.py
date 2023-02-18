# Generated by Django 3.2.18 on 2023-02-18 19:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_id', models.CharField(blank=True, max_length=255, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'ตะกร้าสินค้า',
                'verbose_name_plural': 'ข้อมูลตะกร้าสินค้า',
                'db_table': 'cart',
                'ordering': ['date_added'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=255)),
            ],
            options={
                'verbose_name': 'หมวดหมู่สินค้า',
                'verbose_name_plural': 'ข้อมูลหมวดหมู่สินค้า',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Debtor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone', models.TextField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cash_limit', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'verbose_name': 'ลูกหนี้',
                'verbose_name_plural': 'ข้อมูลลูกหนี้',
                'db_table': 'Debtor',
                'ordering': ['updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money', models.IntegerField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('profit', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('quantity', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'การซื้อสินค้า',
                'verbose_name_plural': 'ข้อมูลการซื้อสินค้า',
                'db_table': 'Order',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.IntegerField()),
                ('image', models.ImageField(upload_to='product')),
                ('active', models.IntegerField(default=1)),
                ('barcode', models.CharField(max_length=255)),
                ('EXP', models.DateField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.category')),
            ],
            options={
                'verbose_name': 'คลังสินค้า',
                'verbose_name_plural': 'ข้อมูลสินค้า',
                'ordering': ['EXP', 'stock'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(max_length=250)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost', models.FloatField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.order')),
            ],
            options={
                'verbose_name': 'รายการสินค้าที่ขาย',
                'verbose_name_plural': 'ข้อมูลรายการสินค้าที่ขาย',
                'db_table': 'OrderItem',
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
            options={
                'verbose_name': 'รายการสินค้า',
                'verbose_name_plural': 'ข้อมูลรายการสินค้า',
                'db_table': 'cartItem',
            },
        ),
    ]
