# Generated by Django 3.2.18 on 2023-03-16 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_product_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='description',
            field=models.CharField(default='', max_length=250),
            preserve_default=False,
        ),
    ]