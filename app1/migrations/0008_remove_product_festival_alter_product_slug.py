# Generated by Django 5.0.1 on 2024-03-10 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0007_alter_product_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='festival',
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]