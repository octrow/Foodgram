# Generated by Django 4.2.5 on 2023-10-09 22:54

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_alter_amountingredient_amount_alter_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#FFFFFF', help_text='Введите HEX-код цвета тега', image_field=None, max_length=7, samples=None, unique=True, verbose_name='HEX-код'),
        ),
    ]
