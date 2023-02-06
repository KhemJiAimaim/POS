# Generated by Django 4.1.3 on 2023-02-06 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_category_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['stock'], 'verbose_name': 'คลังสินค้า', 'verbose_name_plural': 'ข้อมูลสินค้า'},
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='product'),
        ),
    ]
